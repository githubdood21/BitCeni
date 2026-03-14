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



    return jsonArr


if __name__ == "__main__":
    run_scraper("setec.json", "https://setec.mk/%D0%BF%D1%80%D0%B5%D0%BD%D0%BE%D1%81%D0%BD%D0%B8-%D0%BA%D0%BE%D0%BC%D0%BF%D1%98%D1%83%D1%82%D0%B5%D1%80%D0%B8-%D0%B8-%D1%82%D0%B0%D0%B1%D0%BB%D0%B5%D1%82%D0%B8/%D0%BF%D1%80%D0%B5%D0%BD%D0%BE%D1%81%D0%BD%D0%B8-%D0%BA%D0%BE%D0%BC%D0%BF%D1%98%D1%83%D1%82%D0%B5%D1%80%D0%B8", scrape)
