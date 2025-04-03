from math import e, log
from tkinter import Button
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

driver.get('https://ddstore.mk/computersandlaptops/notebooksandaccessories/notebooks.html')

wait = WebDriverWait(driver, 10)

WebDriverWait(driver, 10).until(lambda driver: driver.execute_script("return document.readyState") == "complete")


# dropdown menu
time.sleep(10)

jsonArr = []

dt1 = "name"
dt2 = "price"
dt3 = "link"

index = 1

elems = driver.find_elements(By.CLASS_NAME, "product-item")
while True:
    try:
        productName = elems[index].find_element(By.CLASS_NAME, "product-item-name").text
        productLink = elems[index].find_element(By.CLASS_NAME, "product-item-link").get_attribute("href")
        
        productCost = elems[index].find_element(By.CLASS_NAME, "price").text
        
        elemento = {}

        elemento[dt1] = productName
        elemento[dt2] = productCost.replace(".", "").replace("ден", "")
        elemento[dt3] = productLink

        jsonArr.append(elemento)
        print(f"Selecting product {productName}")
        if index == 47:
            button_menu = driver.find_element(By.CLASS_NAME, 'pages-items')
            driver.execute_script("""
                const element = arguments[0];
                const elementRect = element.getBoundingClientRect();
                const absoluteElementTop = elementRect.top + window.pageYOffset;
                const middle = absoluteElementTop - (window.innerHeight / 2);
                window.scrollTo({ top: middle, behavior: 'smooth' });
            """, button_menu)

            nxt = button_menu.find_element(By.CLASS_NAME, "next")
            time.sleep(5)
            nxt.click()
            index = 0
            time.sleep(10)
            elems = driver.find_elements(By.CLASS_NAME, "product-item")
        index += 1
    except Exception as e:
        print("No more products found.")
        break


time.sleep(3)

with open('data\\ddstore.json', 'w') as json_file:
    json.dump(jsonArr, json_file, indent=4)

driver.quit()