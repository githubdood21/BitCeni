from math import e, log
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import StaleElementReferenceException
import time
import json
import os

options = Options()

options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--headless")  # Uncomment for headless mode
options.set_preference("dom.webdriver.enabled", False)
options.set_preference("useAutomationExtension", False)
options.set_preference("general.useragent.override", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
options.set_preference("permissions.default.image", 2)

service = Service(r'bitceni.scraper/geckodriver/geckodriver.exe')

options.binary_location = r'C:\Program Files\Mozilla Firefox\firefox.exe'

driver = webdriver.Firefox(service=service, options=options)

driver.get('https://hivetec.mk/product-category/laptopprenosnikompjuteri/')

wait = WebDriverWait(driver, 10)

WebDriverWait(driver, 10).until(
    lambda driver: driver.execute_script("return document.readyState") == "complete"
)

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


with open('bitceni.scraper\\data\\hivetec.json', 'w') as json_file:
    json.dump(jsonArr, json_file, indent=4)

driver.quit()