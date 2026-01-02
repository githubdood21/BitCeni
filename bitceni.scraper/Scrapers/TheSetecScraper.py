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

service = Service(r'bitceni.scraper/geckodriver/geckodriver.exe')

options.binary_location = r'C:\Program Files\Mozilla Firefox\firefox.exe'

driver = webdriver.Firefox(service=service, options=options)

driver.get('https://setec.mk/%D0%BF%D1%80%D0%B5%D0%BD%D0%BE%D1%81%D0%BD%D0%B8-%D0%BA%D0%BE%D0%BC%D0%BF%D1%98%D1%83%D1%82%D0%B5%D1%80%D0%B8-%D0%B8-%D1%82%D0%B0%D0%B1%D0%BB%D0%B5%D1%82%D0%B8/%D0%BF%D1%80%D0%B5%D0%BD%D0%BE%D1%81%D0%BD%D0%B8-%D0%BA%D0%BE%D0%BC%D0%BF%D1%98%D1%83%D1%82%D0%B5%D1%80%D0%B8')

wait = WebDriverWait(driver, 10)

WebDriverWait(driver, 10).until(
    lambda driver: driver.execute_script("return document.readyState") == "complete"
)

try:
    # dropdown menu
    time.sleep(5)

    ddm = driver.find_element(By.XPATH, "//*[@id=\"mfilter-content-container\"]/div[2]/div[2]/div[2]/div/select")
    driver.execute_script("""
        const element = arguments[0];
        const elementRect = element.getBoundingClientRect();
        const absoluteElementTop = elementRect.top + window.pageYOffset;
        const middle = absoluteElementTop - (window.innerHeight / 2);
        window.scrollTo({ top: middle, behavior: 'smooth' });
    """, ddm)

    ddm.click()

    time.sleep(1)

    option = driver.find_element(By.XPATH, "//*[@id=\"mfilter-content-container\"]/div[2]/div[2]/div[2]/div/select/option[5]")

    option.click()

    time.sleep(5)

    elems = driver.find_elements(By.CLASS_NAME, "product")

    jsonArr = []

    dt1 = "name"
    dt2 = "price"
    dt3 = "link"

    index = 0

    elems = driver.find_elements(By.CLASS_NAME, "product")
    while True:
        try:
            productName = elems[index].find_element(By.ID, "mora_da_ima_prazno_mesto").text
            productLink = elems[index].find_element(By.ID, "mora_da_ima_prazno_mesto").find_element(By.TAG_NAME, "a").get_attribute("href")
            try:
                productCost = elems[index].find_element(By.CLASS_NAME, "price-new-new").text
            except Exception as p:
                productCost = elems[index].find_element(By.CLASS_NAME, "cena_za_kesh").text
            elemento = {}

            productName = productName.replace("Лаптоп ", "Laptop ")
            productCost = productCost.replace(" Ден.", "")
            productCost = productCost.replace(",", "")

            elemento[dt1] = productName
            elemento[dt2] = productCost
            elemento[dt3] = productLink

            jsonArr.append(elemento)
            print(f"Selecting product {productName}")
            if index == 99:
                button_menu = driver.find_element(By.CLASS_NAME, 'pagination')
                driver.execute_script("""
                    const element = arguments[0];
                    const elementRect = element.getBoundingClientRect();
                    const absoluteElementTop = elementRect.top + window.pageYOffset;
                    const middle = absoluteElementTop - (window.innerHeight / 2);
                    window.scrollTo({ top: middle, behavior: 'smooth' });
                """, button_menu)

                nxt = button_menu.find_element(By.XPATH, "//ul[@class='pagination']/li[last()-1]")
                time.sleep(5)
                nxt.click()
                index = 0
                time.sleep(10)
                elems = driver.find_elements(By.CLASS_NAME, "product")
            index += 1
        except Exception as e:
            print("No more products found.")
            break
except Exception as e:
    print(f"An error occurred: {e}")

time.sleep(3)

with open('bitceni.scraper\\data\\setec.json', 'w') as json_file:
    json.dump(jsonArr, json_file, indent=4)

driver.quit()