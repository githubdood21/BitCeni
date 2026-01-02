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
import re
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

try:
    driver.get('https://www.telekom.mk/dopolnitelna-oprema.nspx?category=13&paymentType=1')

    wait = WebDriverWait(driver, 10)

    WebDriverWait(driver, 10).until(
        lambda driver: driver.execute_script("return document.readyState") == "complete"
    )

    try:
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//*[@id=\"all-cookies-btn\"]"))  # banner that pops up
        )
        time.sleep(2)
        blockBanner = driver.find_element(By.XPATH, "//*[@id=\"all-cookies-btn\"]")
        blockBanner.click()
    except Exception:
        print("No banner!")

    # dropdown menu
    time.sleep(5)

    ddm = driver.find_element(By.XPATH, "//*[@id=\"phone-list\"]/div[1]/div/div/div/div[5]/span/a")
    driver.execute_script("""
        const element = arguments[0];
        const elementRect = element.getBoundingClientRect();
        const absoluteElementTop = elementRect.top + window.pageYOffset;
        const middle = absoluteElementTop - (window.innerHeight / 2);
        window.scrollTo({ top: middle, behavior: 'smooth' });
    """, ddm)

    ddm.click()

    time.sleep(1)

    option = driver.find_element(By.XPATH, "//*[@id=\"phone-list\"]/div[1]/div/div/div/div[5]/span/ul/li[4]/a/div")

    option.click()

    time.sleep(5)

    elems = driver.find_elements(By.CLASS_NAME, "phoneList-box")

    jsonArr = []

    dt1 = "name"
    dt2 = "price"
    dt3 = "link"

    index = 0
    while True:
        try:
            productName = elems[index].find_element(By.CLASS_NAME, "ng-binding").text
            idextract = elems[index].find_element(By.CLASS_NAME, "phone-img")
            productCost = elems[index].find_element(By.CLASS_NAME, "price").text

            theid = re.search(r"id=(\d+)&", idextract.get_attribute("ng-src")).group(1)

            LinkConstruct = "https://www.telekom.mk/accesories-product-details.nspx?deviceId="+ str(theid) +"&quantity=1&paymentType=1"

            elemento = {}

            productCost = productCost.replace(".", "")

            elemento[dt1] = productName
            elemento[dt2] = productCost
            elemento[dt3] = LinkConstruct

            jsonArr.append(elemento)
            print(f"Selecting product {productName}")
            index += 1
        except Exception as e:
            print("No more products found.")
            break
except Exception as e:
    print(f"An error occurred: {e}")

time.sleep(3)

with open('bitceni.scraper\\data\\telekom.json', 'w') as json_file:
    json.dump(jsonArr, json_file, indent=4)

driver.quit()