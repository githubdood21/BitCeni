from math import e, log
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
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

driver.get('https://it.mk/market/filters/product_cat/laptop-prenosni-kompjuteri-2/')

wait = WebDriverWait(driver, 10)

WebDriverWait(driver, 10).until(
    lambda driver: driver.execute_script("return document.readyState") == "complete"
)

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


with open('bitceni.scraper\\data\\itmk.json', 'w') as json_file:
    json.dump(jsonArr, json_file, indent=4)

driver.quit()