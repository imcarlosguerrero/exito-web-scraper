from scraper import initialize_webdriver, get_product

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


"""
react-select-2-option-0 Armenia
react-select-2-option-1 Barranquilla
react-select-2-option-2 Bello
react-select-2-option-3 Bogotá, D.c.
react-select-2-option-4 Bucaramanga
react-select-2-option-5 Buenaventura (Valle del Cauca)
react-select-2-option-6 Cali
react-select-2-option-7 Cartagena De Indias
react-select-2-option-8 Caucasia
react-select-2-option-9 Chía
react-select-2-option-10 Cúcuta
react-select-2-option-11 Duitama
react-select-2-option-12 Envigado
react-select-2-option-13 Florencia (Caquetá)
react-select-2-option-14 Fusagasugá
react-select-2-option-15 Girardot
react-select-2-option-16 Granada (Cundinamarca)
react-select-2-option-17 Granada (Meta)
react-select-2-option-18 Ibagué
react-select-2-option-19 Itagüí
react-select-2-option-20 Jamundí
react-select-2-option-21 La Ceja
react-select-2-option-22 Lorica
react-select-2-option-23 Manizales
react-select-2-option-24 Medellín
react-select-2-option-25 Montería
react-select-2-option-26 Mosquera
react-select-2-option-27 Neiva
react-select-2-option-28 Palmira
react-select-2-option-29 Pasto
react-select-2-option-30 Pereira
react-select-2-option-31 Pitalito (Huila)
react-select-2-option-32 Popayán
react-select-2-option-33 Puerto Berrío (Antioquia)
react-select-2-option-34 Puerto Gaitan (Meta)
react-select-2-option-35 Riohacha (Guajira)
react-select-2-option-36 Rionegro
react-select-2-option-37 Sabaneta
react-select-2-option-38 San Andrés
react-select-2-option-39 San Jerónimo
react-select-2-option-40 San Pedro de los Milagros
react-select-2-option-41 Santa Marta
react-select-2-option-42 Sincelejo
react-select-2-option-43 Soacha
react-select-2-option-44 Soledad
react-select-2-option-45 Tuluá
react-select-2-option-46 Tunja
react-select-2-option-47 Turbaco (Bolívar)
react-select-2-option-48 Turbo
react-select-2-option-49 Valledupar
react-select-2-option-50 Villavicencio
react-select-2-option-51 Zipaquirá

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
        "timestamp": str,
    }

    driver = initialize_webdriver(headless=False)
    products = get_product(
        city={"city_name": "Test City", "city_id": "react-select-2-option-6"},
        store={"store_name": "Test Store", "store_id": "react-select-3-option-0"},
        product_name="Huevo",
    )

    for product in products:
        assert isinstance(product, dict)
        for key, value_type in expected_schema.items():
            assert key in product
            assert isinstance(product[key], value_type)

    driver.quit()


# Run the test
test_get_product_schema()
