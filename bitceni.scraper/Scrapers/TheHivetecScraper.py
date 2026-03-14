import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException

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
            EC.element_to_be_clickable((By.CLASS_NAME, "mfp-close"))  # banner that pops up
        )
        time.sleep(6)
        blockBanner = driver.find_element(By.CLASS_NAME, "mfp-close")
        blockBanner.click()
    except Exception:
        print("No banner!")


    try:
        # click max results
        time.sleep(.5)

        maxno = driver.find_element(By.XPATH, "/html/body/div[2]/div/div/div/div/div/section[2]/div/div[2]/div/section/div/div[2]/div/div[2]/div/div/a[4]")
        maxno.click()

        time.sleep(1)

        jsonArr = []

        while True:
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "wd-product"))
            )
            productCard = driver.find_elements(By.CLASS_NAME, "wd-product")

            # do not, i repeat, do NOT remove this sleep, it will break the code
            time.sleep(4)
            for index in range(len(productCard)):
                time.sleep(.5)
                try:
                    # Re-locate the product card dynamically
                    productCard = driver.find_elements(By.CLASS_NAME, "wd-product")
                    card = productCard[index]

                    driver.execute_script("arguments[0].scrollIntoView();", card)

                    productName = card.find_element(By.CSS_SELECTOR, "h3.wd-entities-title").text.strip()
                    cleanName = productName.replace("[OUTLET]", "").strip()

                    productLink = card.find_element(By.CSS_SELECTOR, "h3.wd-entities-title a").get_attribute("href")

                    try:
                        productPrice = card.find_element(By.XPATH, ".//span[contains(@class, 'price')]/ins").text.strip()
                        cleanPrice = productPrice.replace(",", "").split(".")[0].strip()
                    except Exception:
                        cleanPrice = "N/A"

                    productData = {
                        "name": cleanName,
                        "price": cleanPrice,
                        "link": productLink
                    }

                    print(f"{cleanPrice}, {cleanName}, {productLink}")
                    jsonArr.append(productData)

                except StaleElementReferenceException:
                    print("Stale element encountered. Re-locating...")
                    continue

            # Pagination logic
            try:
                nextButton = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, "next"))
                )
                time.sleep(1)
                nextButton.click()
                time.sleep(5)
            except Exception:
                print("No more pages to scrape.")
                break
    except Exception as e:
        print(f"An error occurred: {e}")




    return jsonArr


if __name__ == "__main__":
    run_scraper("hivetec.json", "https://hivetec.mk/product-category/laptopprenosnikompjuteri/", scrape)
