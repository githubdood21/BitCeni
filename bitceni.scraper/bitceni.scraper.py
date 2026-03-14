import asyncio
import sys
import json
import os
from pathlib import Path
from datetime import datetime

from dotenv import load_dotenv

load_dotenv()

SCRAPERS_DIR = Path(os.getenv("SCRAPERS_DIR", "bitceni.scraper/Scrapers"))
DATA_DIR = Path(os.getenv("DATA_DIR", "bitceni.scraper/data"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "1"))
TIMEOUT_SECONDS = int(os.getenv("TIMEOUT_SECONDS", "60"))  # 5 minutes per scraper
LOG_FILE = Path(os.getenv("LOG_FILE", "log.txt"))


def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {message}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


async def run_script(script_path):
    """Run a single scraper asynchronously with retries and timeout."""
    for attempt in range(1, MAX_RETRIES + 1):
        log(f"Running {script_path.name} (attempt {attempt}/{MAX_RETRIES})")
        try:
            env = os.environ.copy()
            env.setdefault("PYTHONIOENCODING", "utf-8")
            env.setdefault("PYTHONUNBUFFERED", "1")
            proc = await asyncio.create_subprocess_exec(
                sys.executable,
                str(script_path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env
            )

            stdout_chunks = []
            stderr_chunks = []

            async def read_stderr():
                try:
                    while True:
                        line = await proc.stderr.readline()
                        if not line:
                            break
                        stderr_chunks.append(line)
                except asyncio.CancelledError:
                    return

            stderr_task = asyncio.create_task(read_stderr())

            start_time = asyncio.get_event_loop().time()
            sentinel_seen = False
            try:
                while True:
                    if not sentinel_seen:
                        elapsed = asyncio.get_event_loop().time() - start_time
                        remaining = max(0, TIMEOUT_SECONDS - elapsed)
                        if remaining == 0:
                            raise asyncio.TimeoutError
                        line = await asyncio.wait_for(proc.stdout.readline(), timeout=remaining)
                    else:
                        line = await proc.stdout.readline()

                    if not line:
                        break

                    stdout_chunks.append(line)
                    try:
                        decoded_line = line.decode(errors="replace").strip()
                    except Exception:
                        decoded_line = ""
                    if decoded_line == "SCRAPE_DONE":
                        sentinel_seen = True
            except asyncio.TimeoutError:
                log(f"TIMEOUT: {script_path.name} exceeded {TIMEOUT_SECONDS//60} minutes. Killing process...")
                try:
                    proc.terminate()
                    await asyncio.wait_for(proc.wait(), timeout=5)
                except Exception:
                    try:
                        proc.kill()
                        await asyncio.wait_for(proc.wait(), timeout=5)
                    except Exception:
                        # Last resort: kill process tree on Windows
                        try:
                            killer = await asyncio.create_subprocess_exec(
                                "taskkill", "/PID", str(proc.pid), "/T", "/F",
                                stdout=asyncio.subprocess.PIPE,
                                stderr=asyncio.subprocess.PIPE
                            )
                            await killer.communicate()
                        except Exception as kill_exc:
                            log(f"WARNING: Failed to taskkill {script_path.name}: {kill_exc}")
                # Don't hang on stderr task if pipes never close
                if not stderr_task.done():
                    stderr_task.cancel()
                    try:
                        await asyncio.wait_for(stderr_task, timeout=1)
                    except asyncio.CancelledError:
                        pass
                    except Exception:
                        pass
                break

            await proc.wait()
            try:
                await stderr_task
            except asyncio.CancelledError:
                pass

            stdout = b"".join(stdout_chunks)
            stderr = b"".join(stderr_chunks)

            # Decode output safely
            stdout_text = (stdout or b"").decode(errors="replace").strip()
            stderr_text = (stderr or b"").decode(errors="replace").strip()

            if proc.returncode == 0:
                log(f"SUCCESS: {script_path.name}")
                if stdout_text:
                    log(f"Output: {stdout_text}")
                return True
            else:
                log(f"ERROR: {script_path.name} failed on attempt {attempt}")
                if stdout_text:
                    log(f"Output: {stdout_text}")
                if stderr_text:
                    log(f"Error: {stderr_text}")

        except Exception as e:
            log(f"EXCEPTION: {script_path.name} raised an exception on attempt {attempt}")
            log(str(e))

    log(f"FAILED: {script_path.name} failed after {MAX_RETRIES} attempts")
    return False

def scan_json_outputs(expected_count):
    log("Scanning JSON output files")

    empty_files = []
    empty_arrays = []

    if not DATA_DIR.exists():
        log("WARNING: data folder does not exist")
        return empty_files, empty_arrays

    json_files = list(DATA_DIR.glob("*.json"))

    for jf in json_files:
        try:
            if jf.stat().st_size == 0:
                empty_files.append(jf.name)
                continue

            with open(jf, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list) and len(data) == 0:
                    empty_arrays.append(jf.name)

        except Exception as e:
            log(f"WARNING: Could not read {jf.name}: {e}")

    log(f"JSON files found: {len(json_files)} / {expected_count}")

    if empty_files:
        log("Empty JSON files:")
        for f in empty_files:
            log(f"  - {f}")

    if empty_arrays:
        log("JSON files with empty arrays:")
        for f in empty_arrays:
            log(f"  - {f}")

    if not empty_files and not empty_arrays:
        log("All JSON outputs look valid")

    return empty_files, empty_arrays


def find_script_for_output(output_filename, scripts):
    output_stem = Path(output_filename).stem.lower()
    for script in scripts:
        if output_stem and output_stem in script.stem.lower():
            return script.name
    return None


def write_metadata_json(total_scripts, successes, failures, empty_files, empty_arrays):
    DATA_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    snapshots_dir = DATA_DIR / "snapshots"
    snapshots_dir.mkdir(exist_ok=True)
    metadata_file = snapshots_dir / f"snapshot-{timestamp}.json"

    metadata = {
        "run_timestamp": timestamp,
        "total_scrapers": total_scripts,
        "succeeded": successes,
        "failed": failures,
        "empty_json_files": empty_files,
        "empty_json_arrays": empty_arrays
    }

    with open(metadata_file, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    log(f"Metadata written to {metadata_file.name}")


async def main():
    # Reset log file
    LOG_FILE.write_text("", encoding="utf-8")
    log("===== SCRAPER RUN STARTED =====")

    scripts = sorted(
        s for s in SCRAPERS_DIR.glob("*.py")
        if s.name != Path(__file__).name
    )

    successes = []
    failures = []

    for script in scripts:
        try:
            success = await run_script(script)
            if success:
                successes.append(script.name)
            else:
                failures.append(script.name)
        except Exception as e:
            log(f"UNEXPECTED ERROR: {script.name} caused an exception in the manager")
            log(str(e))
            failures.append(script.name)

    log("===== RUN SUMMARY =====")
    log(f"Total scrapers run: {len(scripts)}")
    log(f"Succeeded: {len(successes)}")
    log(f"Failed: {len(failures)}")

    if successes:
        log("Successful scrapers:")
        for s in successes:
            log(f"  - {s}")

    if failures:
        log("Failed scrapers:")
        for f in failures:
            log(f"  - {f}")

    empty_files, empty_arrays = scan_json_outputs(len(scripts))
    failed_due_to_output = set()
    for output_name in empty_files + empty_arrays:
        matched_script = find_script_for_output(output_name, scripts)
        if matched_script:
            failed_due_to_output.add(matched_script)

    if failed_due_to_output:
        successes = [s for s in successes if s not in failed_due_to_output]
        for s in sorted(failed_due_to_output):
            if s not in failures:
                failures.append(s)
        log("Reclassified scrapers as FAILED due to empty output:")
        for s in sorted(failed_due_to_output):
            log(f"  - {s}")

    write_metadata_json(len(scripts), successes, failures, empty_files, empty_arrays)

    log("===== SCRAPER RUN FINISHED =====")


if __name__ == "__main__":
    asyncio.run(main())
