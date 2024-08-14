from web_scraper import initialize_webdriver, get_product

"""
This test ensures that the get_product function returns a list of dictionaries with the correct schema for the product data.

The schema for the product data is as follows:
{
    "city": str,
    "store": str,
    "url": str,
    "name": str,
    "price": str,
    "discount": float,
    "image": str,
    "timestamp": str
}

The test initializes a webdriver, gets the product data for a specific product, and then checks that each product in the list has the correct schema.

If the test passes, the function is correctly extracting the product data from the website and returning it in the expected format.

If the test fails, there may be an issue with the extraction or formatting of the product data, most likely, something changed in the website and the scraper is broken.
"""
def test_get_product_schema():
    expected_schema = {
        "city": str,
        "store": str,
        "url": str,
        "name": str,
        "price": str,
        "discount": float,
        "image": str,
        "timestamp": str
    }

    driver = initialize_webdriver(headless=False)
    products = get_product(driver=driver, city={"city_name": "Test City", "city_id": "react-select-2-option-0"}, store={"store_name": "Test Store", "store_id": "react-select-3-option-0"}, product_name="Huevo")

    for product in products:
        assert isinstance(product, dict)
        for key, value_type in expected_schema.items():
            assert key in product
            assert isinstance(product[key], value_type)

    driver.quit()