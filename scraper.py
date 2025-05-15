from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from datetime import datetime, timezone
from selenium.webdriver.common.by import By
from selenium import webdriver
from bs4 import BeautifulSoup
import ua_generator
import platform as pf
import time
import csv
import os


def generate_random_user_agent():
    device = "desktop"
    platform = ("windows", "macos")
    browser = ("chrome", "edge")

    user_agent = ua_generator.generate(
        device=device, browser=browser, platform=platform
    ).text

    return user_agent


def initialize_webdriver(headless=True):
    user_agent = generate_random_user_agent()

    options = Options()
    options.add_argument(f'user-agent="{user_agent}"')
    if headless:
        options.add_argument("--headless=new")

    chromedriver_install = ChromeDriverManager().install()
    webdriver_folder = os.path.dirname(chromedriver_install)
    chromedriver_filename = (
        "chromedriver.exe" if pf.system() == "Windows" else "chromedriver"
    )
    chromedriver_path = os.path.join(webdriver_folder, chromedriver_filename)
    webdriver_service = Service(chromedriver_path)
    driver = webdriver.Chrome(service=webdriver_service, options=options)

    return driver


def click_select_city_button(driver):
    select_city_and_store_button = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.XPATH, "/html/body/div/header/section/div/div[1]/div[3]/button")
        )
    )

    select_city_and_store_button.click()

    select_city_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="react-select-2-input"]'))
    )

    select_city_button.click()


def get_city_list(driver):
    city_list = []

    driver.get("https://www.exito.com/s")

    click_select_city_button(driver=driver)

    city_listbox = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="react-select-2-listbox"]'))
    )

    city_options = city_listbox.find_elements(By.XPATH, './/div[@role="option"]')

    for city_option in city_options:
        city_option_name = city_option.text
        city_option_id = city_option.get_attribute("id")
        city_list.append({"city_name": city_option_name, "city_id": city_option_id})

    return city_list


def click_selected_city_button(driver, city_id, path="https://www.exito.com/s"):
    driver.get(path)

    click_select_city_button(driver=driver)

    city_listbox = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="react-select-2-listbox"]'))
    )

    city_options = city_listbox.find_elements(By.XPATH, './/div[@role="option"]')

    for city_option in city_options:
        if city_option.get_attribute("id") == city_id:
            city_option.click()
            return True

    return False


def click_select_store_button(driver):
    select_store_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="react-select-3-input"]'))
    )

    select_store_button.click()


def get_store_list(driver, city_id):
    store_list = []

    click_selected_city_button(driver=driver, city_id=city_id)

    click_select_store_button(driver=driver)

    store_listbox = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="react-select-3-listbox"]'))
    )

    store_options = store_listbox.find_elements(By.XPATH, './/div[@role="option"]')

    for store_option in store_options:
        store_option_name = store_option.text
        store_option_id = store_option.get_attribute("id")
        store_list.append(
            {"store_name": store_option_name, "store_id": store_option_id}
        )

    return store_list


def click_selected_store_button(driver, store_id):
    click_select_store_button(driver=driver)

    store_listbox = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="react-select-3-listbox"]'))
    )

    store_options = store_listbox.find_elements(By.XPATH, './/div[@role="option"]')

    for store_option in store_options:
        if store_option.get_attribute("id") == store_id:
            store_option.click()
            return True

    return False


def click_submit_button(driver):
    # It'd be better to use a more general selector for the submit button in case the class name changes in the future.
    submit_button = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.CLASS_NAME, "PickupPoint_primaryButtonEnable__vh9yw")
        )
    )

    submit_button.click()


def get_product(city, store, product_name, sipsa_name):
    driver = initialize_webdriver(headless=False)
    products = []

    try:
        click_selected_city_button(
            path=f"https://www.exito.com/s?q={product_name}&category-1=mercado&facets=category-1&sort=score_desc&page=0",
            driver=driver,
            city_id=city["city_id"],
        )
        click_selected_store_button(driver=driver, store_id=store["store_id"])
        click_submit_button(driver=driver)

        time.sleep(5)

        soup = BeautifulSoup(driver.page_source, "html.parser")

        empty_state = soup.find(
            "section", {"data-fs-empty-state": "true"}
        ) or soup.find("div", {"data-fs-empty-gallery-container": "true"})

        if empty_state:
            print(
                f"Product '{product_name}' not found in {city['city_name']} at {store['store_name']}"
            )
            # Return an empty result with metadata
            return [
                {
                    "city": city["city_name"],
                    "store": store["store_name"],
                    "product_name": product_name,
                    "sipsa_name": sipsa_name,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "products": [],
                }
            ]

        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "div[data-fs-product-card-image='true']")
            )
        )

        soup = BeautifulSoup(driver.page_source, "html.parser")

        ul_content = soup.find(
            "ul", {"data-fs-product-grid": "true", "data-fs-product-grid-list": "true"}
        )

        if not ul_content:
            print(
                f"No product grid found for '{product_name}' in {city['city_name']} at {store['store_name']}"
            )
            return [
                {
                    "city": city["city_name"],
                    "store": store["store_name"],
                    "product_name": product_name,
                    "sipsa_name": sipsa_name,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "products": [],
                }
            ]

        article_elements = ul_content.find_all("li")

        for article in article_elements:
            url = article.find("a", {"data-testid": "product-link"})["href"]
            name = article.find("h3").text.strip()
            image = (
                article.find("div", {"data-fs-product-card-image": "true"})
                .find("a", {"data-testid": "product-link"})
                .find("img")["src"]
            )
            price = (
                article.find("div", {"data-fs-container-price-otros-geral": "true"})
                .find("p")
                .text.strip()
            )
            try:
                product_links = article.find_all("a", {"data-testid": "product-link"})
                if len(product_links) > 1 and product_links[1].find("span"):
                    unit_price = (
                        product_links[1]
                        .find("span")
                        .text.strip()
                        .replace("(", "")
                        .replace(")", "")
                    )
                else:
                    unit_price = "N/A"
            except Exception:
                unit_price = "N/A"

            try:
                discount = (
                    article.find("div", {"data-fs-product-card-prices": "true"})
                    .find("span", {"data-percentage": "true"})
                    .text.strip()
                )
            except AttributeError:
                discount = 0

            products.append(
                {
                    "city": city["city_name"],
                    "store": store["store_name"],
                    "url": "https://www.exito.com" + url,
                    "name": name,
                    "price": price,
                    "unit_price": unit_price,
                    "discount": float(discount),
                    "image": image,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "exito_name": product_name,
                    "sipsa_name": sipsa_name,
                }
            )

        # Create a structured result
        result = {
            "city": city["city_name"],
            "store": store["store_name"],
            "product_name": product_name,
            "sipsa_name": sipsa_name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "products": products,
        }

        # Write to CSV
        with open(
            os.path.join("results", "products.csv"), "a", newline="", encoding="utf-8"
        ) as csvfile:
            fieldnames = [
                "city",
                "store",
                "url",
                "name",
                "price",
                "unit_price",
                "discount",
                "image",
                "timestamp",
                "exito_name",
                "sipsa_name",
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            for product in products:
                writer.writerow(
                    {
                        "city": product["city"],
                        "store": product["store"],
                        "url": product["url"],
                        "name": product["name"],
                        "price": product["price"],
                        "unit_price": product["unit_price"],
                        "discount": product["discount"],
                        "image": product["image"],
                        "timestamp": product["timestamp"],
                        "exito_name": product_name,
                        "sipsa_name": sipsa_name,
                    }
                )

        return result

    except Exception as e:
        print(f"Error scraping product '{product_name}': {e}")
        # Return an empty result on error
        return [
            {
                "city": city["city_name"],
                "store": store["store_name"],
                "product_name": product_name,
                "sipsa_name": sipsa_name,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "products": [],
            }
        ]

    finally:
        driver.quit()
