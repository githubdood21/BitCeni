import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from pathlib import Path
import sys

SCRAPER_ROOT = Path(__file__).resolve().parents[1]
if str(SCRAPER_ROOT) not in sys.path:
    sys.path.append(str(SCRAPER_ROOT))

from scraper_base import run_scraper, wait_for_page_ready




def scrape(driver):
    jsonArr = []


    wait = WebDriverWait(driver, 10)

    wait_for_page_ready(driver, 10)

    try:
        WebDriverWait(driver, 6).until(
            EC.element_to_be_clickable((By.XPATH, "/html/body/div/div[6]/div/div/button[2]"))  # banner that pops up
        )
        time.sleep(2)
        blockBanner = driver.find_element(By.XPATH, "/html/body/div/div[6]/div/div/button[2]")
        blockBanner.click()
    except Exception:
        print("No banner!")

    time.sleep(2)

    jsonArr = []

    try:
        while True:
            WebDriverWait(driver, 10).until( # await load all cards
                EC.presence_of_all_elements_located((By.CLASS_NAME, "ais-Hits-item"))
            )
            productCard = driver.find_elements(By.CLASS_NAME, "ais-Hits-item")

            for card in productCard:
                driver.execute_script("arguments[0].scrollIntoView();", card)
                productName = card.find_element(By.CLASS_NAME, "sc-14no49n-0").text.strip()
                cleanName = productName.replace("Лаптоп ", "").strip()

                productLink = card.find_element(By.CLASS_NAME, "sc-492kdg-0").get_attribute("href")

                try:
                    productPrice = card.find_element(By.CLASS_NAME, "sc-1arj7wv-2").text.strip()
                    cleanPrice = productPrice.replace(".", "").split("ден")[0].strip()

                except Exception:
                    cleanPrice = "N/A"

                productData = {
                    "name": cleanName,
                    "price": cleanPrice,
                    "link": productLink
                }

                print(f"{cleanPrice}, {cleanName}, {productLink}") # print product name in consoles

                jsonArr.append(productData)

            try:
                nextButton = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "/html/body/div/div[3]/div[3]/div/div[3]/div[3]/ul/li[3]/a"))
                )
                time.sleep(1)  # wait for the button to be clickable
                nextButton.click()
                time.sleep(5) # wait for page to load
            except Exception:
                print("No more pages to scrape.")
                break
    except Exception as e:
        print(f"An error occurred: {e}")




    return jsonArr


if __name__ == "__main__":
    run_scraper("ananas.json", "https://ananas.mk/kategorii/it-shop/kompjuteri-i-kompjuterska-oprema/laptopi", scrape)
