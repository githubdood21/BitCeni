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
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "/html/body/div[3]/div[2]/div/div/div/div/button"))  # banner that pops up
        )
        time.sleep(2)
        blockBanner = driver.find_element(By.XPATH, "/html/body/div[3]/div[2]/div/div/div/div/button")
        blockBanner.click()
    except Exception:
        print("No banner!")



    try:
        # dropdown menu
        time.sleep(.5)

        ddm = driver.find_element(By.XPATH, "/html/body/div[3]/section[3]/div/div/div[2]/div/div[1]/div[2]/div[2]/div[3]/div")
        ddm.click()

        # select '50' results
        time.sleep(.5)

        fifty = driver.find_element(By.XPATH, "/html/body/div[3]/section[3]/div/div/div[2]/div/div[1]/div[2]/div[2]/div[3]/div/ul/li[5]")
        fifty.click()

        time.sleep(1)

        jsonArr = []

        while True:
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "product-card"))
            )
            productCard = driver.find_elements(By.CLASS_NAME, "product-card")

            for card in productCard:
                driver.execute_script("arguments[0].scrollIntoView();", card)
                productName = card.find_element(By.CLASS_NAME, "product-name").text.strip()
                cleanName = productName.replace("[OUTLET]", "").strip()

                productLink = card.find_element(By.CLASS_NAME, "product-name").get_attribute("href")

                try:
                    productPrice = card.find_element(By.XPATH, ".//div[contains(@class, 'product-card-bottom')]//div[contains(@class, 'product-price')]").text.strip()
                    cleanPrice = productPrice.replace(".", "").split(",")[0].strip()

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
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'page-link')]/i[contains(@class, 'la-angle-right')]"))
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
    run_scraper("anhoch.json", "https://www.anhoch.com/categories/site-laptopi/products", scrape)
