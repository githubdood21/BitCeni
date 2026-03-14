import time
import re

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

    try:

        wait = WebDriverWait(driver, 10)

        wait_for_page_ready(driver, 10)

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



    return jsonArr


if __name__ == "__main__":
    run_scraper("telekom.json", "https://www.telekom.mk/dopolnitelna-oprema.nspx?category=13&paymentType=1", scrape)
