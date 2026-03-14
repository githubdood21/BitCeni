import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

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
        time.sleep(10)

        ddm = driver.find_element(By.ID, "input-limit")
        driver.execute_script("""
            const element = arguments[0];
            const elementRect = element.getBoundingClientRect();
            const absoluteElementTop = elementRect.top + window.pageYOffset;
            const middle = absoluteElementTop - (window.innerHeight / 2);
            window.scrollTo({ top: middle, behavior: 'smooth' });
        """, ddm)

        ddm.click()

        time.sleep(1)

        option = driver.find_element(By.XPATH, "//*[@id=\"input-limit\"]/option[5]")

        option.click()

        time.sleep(5)

        jsonArr = []

        dt1 = "name"
        dt2 = "price"
        dt3 = "link"

        index = 1

        elems = driver.find_elements(By.CLASS_NAME, "product-layout")
        while True:
            try:
                productName = elems[index].find_element(By.CLASS_NAME, "name").find_element(By.TAG_NAME, "a").text
                productLink = elems[index].find_element(By.CLASS_NAME, "name").find_element(By.TAG_NAME, "a").get_attribute("href")

                productCost = elems[index].find_element(By.CLASS_NAME, "price-normal").text

                elemento = {}

                elemento[dt1] = productName
                elemento[dt2] = productCost.replace(",", "").replace("ден.", "")
                elemento[dt3] = productLink

                jsonArr.append(elemento)
                print(f"Selecting product {productName}")
                if index == 99:
                    button_menu = driver.find_element(By.CLASS_NAME, 'pagination-results')
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
                    elems = driver.find_elements(By.CLASS_NAME, "product-layout")
                index += 1
            except Exception as e:
                print("No more products found.")
                break
    except Exception as e:
        print(f"An error occurred: {e}")

    time.sleep(3)



    return jsonArr


if __name__ == "__main__":
    run_scraper("laptopimk.json", "https://www.laptop.mk/laptops", scrape)
