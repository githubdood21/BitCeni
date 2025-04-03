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

service = Service(r'geckodriver-v0.35.0-win32/geckodriver.exe')

options.binary_location = r'C:\Program Files\Mozilla Firefox\firefox.exe'

driver = webdriver.Firefox(service=service, options=options)

driver.get('https://gjirafa50.mk/za-biznis-laptop?is=true')

wait = WebDriverWait(driver, 10)

WebDriverWait(driver, 10).until(
    lambda driver: driver.execute_script("return document.readyState") == "complete"
)

jsonArr = []
processed_cards = set()  # Keep track of processed product cards

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

with open('data\\gjirafaB.json', 'w') as json_file:
    json.dump(jsonArr, json_file, indent=4)

driver.quit()
