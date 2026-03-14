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

    jsonArr = []  # create an empty json array to store the data

    try:
        while True:
            WebDriverWait(driver, 10).until( # await load all cards
                EC.presence_of_all_elements_located((By.CLASS_NAME, "product"))
            )
            productCard = driver.find_elements(By.CLASS_NAME, "product")

            for card in productCard:
                driver.execute_script("arguments[0].scrollIntoView();", card)
                productName = card.find_element(By.CLASS_NAME, "woocommerce-loop-product__title").text.strip()
                cleanName = productName.replace("\u2033", "")

                productLink = card.find_element(By.CLASS_NAME, "woocommerce-loop-product__link").get_attribute("href")

                try:
                    productPrice = card.find_element(By.CLASS_NAME, "price").text.strip() # locate parent of price by classname
                    cleanPrice = productPrice.replace(".", "").split("ден")[0].strip() # clean the price

                except Exception:
                    cleanPrice = "N/A"

                productData = {
                    "name": cleanName,
                    "price": cleanPrice,
                    "link": productLink
                }

                print(f"{cleanPrice}, {productName}, {productLink}") # print product name in consoles

                jsonArr.append(productData)

            try:
                nextButton = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, "next"))
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
    run_scraper("itmk.json", "https://it.mk/market/filters/product_cat/laptop-prenosni-kompjuteri-2/", scrape)
