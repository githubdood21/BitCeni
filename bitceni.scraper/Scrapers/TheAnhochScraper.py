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

driver.get('https://www.anhoch.com/categories/site-laptopi/products')

wait = WebDriverWait(driver, 10)

WebDriverWait(driver, 10).until(
    lambda driver: driver.execute_script("return document.readyState") == "complete"
)

try:
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "/html/body/div[3]/div[2]/div/div/div/div/button"))  # banner that pops up
    )
    time.sleep(2)
    blockBanner = driver.find_element(By.XPATH, "/html/body/div[3]/div[2]/div/div/div/div/button")
    blockBanner.click()
except Exception:
    print("No banner!")



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



with open('data\\anhoch.json', 'w') as json_file:
    json.dump(jsonArr, json_file, indent=4)

driver.quit()