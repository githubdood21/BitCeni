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

        ddm = driver.find_element(By.XPATH, "//*[@id=\"affix2\"]/div/div[1]/div[2]/select")
        driver.execute_script("""
            const element = arguments[0];
            const elementRect = element.getBoundingClientRect();
            const absoluteElementTop = elementRect.top + window.pageYOffset;
            const middle = absoluteElementTop - (window.innerHeight / 2);
            window.scrollTo({ top: middle, behavior: 'smooth' });
        """, ddm)

        ddm.click()

        time.sleep(1)

        option = driver.find_element(By.XPATH, "//*[@id=\"affix2\"]/div/div[1]/div[2]/select/option[5]")

        option.click()

        time.sleep(5)

        jsonArr = []

        dt1 = "name"
        dt2 = "price"
        dt3 = "link"

        index = 1

        elems = driver.find_elements(By.CLASS_NAME, "white-box")
        while True:
            try:
                productName = elems[index].find_element(By.CLASS_NAME, "product-list-item__content--title").text
                productLink = elems[index].find_element(By.TAG_NAME, "a").get_attribute("href")

                productCost = elems[index].find_elements(By.CLASS_NAME, "product-price__amount--value")

                cenu = 0

                if len(productCost) == 3:
                    cenu = productCost[1].text
                else:
                    cenu = productCost[0].text

                elemento = {}

                elemento[dt1] = productName
                elemento[dt2] = cenu.replace(".", "")
                elemento[dt3] = productLink

                jsonArr.append(elemento)
                print(f"Selecting product {productName}")
                if index == 99:
                    button_menu = driver.find_element(By.XPATH, '//*[@id="mainContainer"]/div/div[3]/div[104]/div')
                    driver.execute_script("""
                        const element = arguments[0];
                        const elementRect = element.getBoundingClientRect();
                        const absoluteElementTop = elementRect.top + window.pageYOffset;
                        const middle = absoluteElementTop - (window.innerHeight / 2);
                        window.scrollTo({ top: middle, behavior: 'smooth' });
                    """, button_menu)

                    nxt = button_menu.find_element(By.XPATH, "//*[@id=\"mainContainer\"]/div/div[3]/div[104]/div/ul/li[5]/a")
                    time.sleep(5)
                    nxt.click()
                    index = 0
                    time.sleep(10)
                    elems = driver.find_elements(By.CLASS_NAME, "white-box")
                index += 1
            except Exception as e:
                print("No more products found.")
                break
    except Exception as e:
        print(f"An error occurred: {e}")


    time.sleep(3)



    return jsonArr


if __name__ == "__main__":
    run_scraper("neptun.json", "https://www.neptun.mk/prenosni_kompjuteri.nspx", scrape)
