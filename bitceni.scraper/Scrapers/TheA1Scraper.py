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

driver.get('https://www.a1.mk/webshop/mk/laptopsandtablets/laptop')

wait = WebDriverWait(driver, 10)

WebDriverWait(driver, 10).until(
    lambda driver: driver.execute_script("return document.readyState") == "complete"
)

try:
    WebDriverWait(driver, 6).until(
        EC.element_to_be_clickable((By.ID, "onetrust-reject-all-handler"))  # reject cookies
    )
    time.sleep(2)
    blockBanner = driver.find_element(By.ID, "onetrust-reject-all-handler")
    blockBanner.click()
except Exception:
    print("No cookies!")

jsonArr = []

while True:
    WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, "dvc-idtfr"))
    )

    try:
        showMoreBtn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "showMore"))
        )
        time.sleep(1)  # wait for the button to be clickable
        showMoreBtn.click()
        time.sleep(4) # wait for page to load
    except Exception:
        print("No more to show.")
        break

    productCard = driver.find_elements(By.CLASS_NAME, "dvc-idtfr")

    for card in productCard:
        driver.execute_script("arguments[0].scrollIntoView();", card)
        productName = card.find_element(By.CLASS_NAME, "brand-name").text.strip()
        cleanName = productName.replace("\n", " ").strip()

        productLink = card.find_element(By.CLASS_NAME, "device-link").get_attribute("href")
    
        try:
            productPrice = card.find_element(By.CLASS_NAME, "cena").text.strip()
            cleanPrice = productPrice.replace(".", "").split("ден")[0].strip()
            intedPrice = int(cleanPrice)
            cleanPrice = intedPrice * 24
    
        except Exception:
            cleanPrice = "N/A"
    
        productData = {
            "name": cleanName,
            "price": cleanPrice,
            "link": productLink
        }
        
        print(f"{cleanPrice}, {productName}, {productLink}") # print product name in consoles
    
        jsonArr.append(productData)



with open('data\\a1.json', 'w') as json_file:
    json.dump(jsonArr, json_file, indent=4)

driver.quit()