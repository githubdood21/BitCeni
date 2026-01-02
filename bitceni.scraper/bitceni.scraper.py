import asyncio
import sys
import json
from pathlib import Path
from datetime import datetime

SCRAPERS_DIR = Path("bitceni.scraper/Scrapers")
DATA_DIR = Path("bitceni.scraper/data")
MAX_RETRIES = 1
TIMEOUT_SECONDS = 60  # 5 minutes per scraper
LOG_FILE = Path("log.txt")


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
            proc = await asyncio.create_subprocess_exec(
                sys.executable,
                str(script_path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            try:
                # Wait for the process to finish, with timeout
                stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=TIMEOUT_SECONDS)
            except asyncio.TimeoutError:
                log(f"TIMEOUT: {script_path.name} exceeded {TIMEOUT_SECONDS//60} minutes. Killing process...")
                proc.kill()
                break

            # Decode output safely
            stdout_text = (stdout or b"").decode().strip()
            stderr_text = (stderr or b"").decode().strip()

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


def write_metadata_json(total_scripts, successes, failures, empty_files, empty_arrays):
    DATA_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    metadata_file = DATA_DIR / f"{timestamp}.json"

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
    write_metadata_json(len(scripts), successes, failures, empty_files, empty_arrays)

    log("===== SCRAPER RUN FINISHED =====")


if __name__ == "__main__":
    asyncio.run(main())