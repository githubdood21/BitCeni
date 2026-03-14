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

    jsonArr = []
    processed_cards = set()  # Keep track of processed product cards

    try:
        while True:
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "item-box"))
            )

            try:
                showMoreBtn = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, "load-more-products-btn"))
                )
                time.sleep(1)  # Wait for the button to be clickable
                showMoreBtn.click()
                time.sleep(5)  # Wait for page to load
            except Exception:
                print("No more to show.")
                break

            productCard = driver.find_elements(By.CLASS_NAME, "item-box")

            for card in productCard:
                card_id = card.get_attribute("data-position")  # Use a unique identifier for each card if available
                if card_id in processed_cards:
                    continue  # Skip already processed cards

                processed_cards.add(card_id)  # Mark this card as processed

                productName = card.find_element(By.CLASS_NAME, "product-title").text.strip()
                cleanName = productName.replace("\n", " ").replace("Laptop", "").replace("Лаптоп", "").strip()

                productLink = card.find_element(By.CSS_SELECTOR, "div section.details h3.product-title a").get_attribute("href")

                try:
                    productPrice = card.find_element(By.CLASS_NAME, "price").text.strip()
                    cleanPrice = productPrice.replace(",", "").split("MKD")[0].strip()
                except Exception:
                    cleanPrice = "N/A"

                productData = {
                    "name": cleanName,
                    "price": cleanPrice,
                    "link": productLink
                }

                print(f"{cleanPrice}, {productName}, {productLink}")  # Print product name in console

                jsonArr.append(productData)
    except Exception as e:
        print(f"An error occurred: {e}")



    return jsonArr


if __name__ == "__main__":
    run_scraper("gjirafaS.json", "https://gjirafa50.mk/za-uchilishte-laptop?is=true", scrape)
