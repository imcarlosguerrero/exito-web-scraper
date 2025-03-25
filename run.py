from app import get_product
from concurrent.futures import ProcessPoolExecutor
from motor.motor_asyncio import AsyncIOMotorClient
from data_processing.models.food import Food
from beanie import init_beanie
import json
import asyncio
import os


async def initialize_motor():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    await init_beanie(
        database=client["foodprice"],
        document_models=[Food],
    )


async def get_food_data():
    await initialize_motor()
    food_data = await Food.find_all().to_list(length=None)
    return food_data


food_data = asyncio.run(get_food_data())
products = {food.exito_name for food in food_data}


def clean_results_folder():
    results_folder = "results"
    if not os.path.exists(results_folder):
        return

    for filename in os.listdir(results_folder):
        if filename.endswith(".json"):
            product_name = filename[:-5]
            if product_name not in products:
                file_path = os.path.join(results_folder, filename)
                os.remove(file_path)
                print(f"Deleted {file_path}")


def scrape_product(product):
    print(f"Getting {product}...")

    json_file_path = os.path.join("results", f"{product}.json")
    if os.path.exists(json_file_path):
        print(f"JSON file for {product} already exists. Skipping scraping.")
        with open(json_file_path, "r", encoding="utf-8") as f:
            products = json.load(f)
        return products

    get_product(
        city={"city_name": "Cali", "city_id": "react-select-2-option-6"},
        store={
            "store_name": "Exito Wow Valle del Lili",
            "store_id": "react-select-3-option-7",
        },
        product_name=product,
    )


if __name__ == "__main__":
    clean_results_folder()

    with ProcessPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(scrape_product, product) for product in products]
        for future in futures:
            future.result()
