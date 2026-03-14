import os
import json
import sys
from pathlib import Path
from typing import Any, Iterable

from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait


DATA_DIR = Path(os.getenv("DATA_DIR", "bitceni.scraper/data"))
GECKODRIVER_PATH = os.getenv("GECKODRIVER_PATH", "bitceni.scraper/geckodriver/geckodriver.exe")
FIREFOX_BINARY = os.getenv("FIREFOX_BINARY", r"C:\Program Files\Mozilla Firefox\firefox.exe")
USER_AGENT = os.getenv(
    "SCRAPER_USER_AGENT",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def create_firefox_driver(headless: bool = True) -> webdriver.Firefox:
    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled")
    if headless:
        options.add_argument("--headless")
    options.set_preference("dom.webdriver.enabled", False)
    options.set_preference("useAutomationExtension", False)
    options.set_preference("general.useragent.override", USER_AGENT)
    options.set_preference("permissions.default.image", 2)
    options.binary_location = FIREFOX_BINARY

    service = Service(GECKODRIVER_PATH)
    return webdriver.Firefox(service=service, options=options)


def wait_for_page_ready(driver: webdriver.Firefox, timeout: int = 10) -> None:
    WebDriverWait(driver, timeout).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )


def run_scraper(output_name: str, url: str, scrape_fn, headless: bool = True, ready_timeout: int = 10):
    driver = create_firefox_driver(headless=headless)
    try:
        driver.get(url)
        wait_for_page_ready(driver, ready_timeout)
        data = scrape_fn(driver)
        if data is None:
            data = []
        print("SCRAPE_DONE", flush=True)
        write_json(data, output_name)
        return data
    finally:
        try:
            driver.quit()
        except Exception:
            pass


def write_json(data: Iterable[Any], filename: str) -> Path:
    DATA_DIR.mkdir(exist_ok=True)
    output_path = DATA_DIR / filename
    with open(output_path, "w", encoding="utf-8") as json_file:
        json.dump(list(data), json_file, indent=4, ensure_ascii=False)
    return output_path
