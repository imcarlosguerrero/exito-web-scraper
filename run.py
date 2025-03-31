from app import get_product
from concurrent.futures import ProcessPoolExecutor
from motor.motor_asyncio import AsyncIOMotorClient
from data_processing.models.food import Food
from beanie import init_beanie
import json
import asyncio
import os

# Dictionary of cities and stores with their IDs
CITIES_AND_STORES = {
    "Bogotá": {
        "city_id": "react-select-2-option-3",
        "stores": [
            {
                "store_name": "Éxito Chapinero",
                "store_id": "react-select-3-option-4",
            },
            {
                "store_name": "Éxito Gran Estación",
                "store_id": "react-select-3-option-9",
            },
            {"store_name": "Éxito Bosa", "store_id": "react-select-3-option-2"},
        ],
    },
    "Medellín": {
        "city_id": "react-select-2-option-24",
        "stores": [
            {
                "store_name": "Éxito Poblado",
                "store_id": "react-select-3-option-6",
            },
            {"store_name": "Éxito San Antonio", "store_id": "react-select-3-option-8"},
            {
                "store_name": "Éxito Unicentro Medellín",
                "store_id": "react-select-3-option-9",
            },
        ],
    },
    "Cali": {
        "city_id": "react-select-2-option-6",
        "stores": [
            {
                "store_name": "Éxito Valle de Lili",
                "store_id": "react-select-3-option-7",
            },
            {
                "store_name": "Éxito San Fernando",
                "store_id": "react-select-3-option-5",
            },
            {
                "store_name": "Éxito Melendez",
                "store_id": "react-select-3-option-7",
            },
        ],
    },
    "Barranquilla": {
        "city_id": "react-select-2-option-1",
        "stores": [
            {
                "store_name": "Éxito Barranquilla",
                "store_id": "react-select-3-option-0",
            },
            {
                "store_name": "Éxito Panorama",
                "store_id": "react-select-3-option-2",
            },
            {
                "store_name": "Éxito Metropolitano",
                "store_id": "react-select-3-option-1",
            },
        ],
    },
    "Bucaramanga": {
        "city_id": "react-select-2-option-4",
        "stores": [
            {
                "store_name": "Éxito Cañaveral",
                "store_id": "react-select-3-option-0",
            },
            {
                "store_name": "Éxito La Rosita",
                "store_id": "react-select-3-option-1",
            },
            {
                "store_name": "Éxito Oriental",
                "store_id": "react-select-3-option-2",
            },
        ],
    },
    "Cartagena": {
        "city_id": "react-select-2-option-7",
        "stores": [
            {"store_name": "Éxito Cartagena", "store_id": "react-select-3-option-0"},
            {"store_name": "Éxito Castellana", "store_id": "react-select-3-option-1"},
            {"store_name": "Éxito San Diego", "store_id": "react-select-3-option-2"},
        ],
    },
    "Cúcuta": {
        "city_id": "react-select-2-option-10",
        "stores": [
            {
                "store_name": "Éxito Avenida Quinta",
                "store_id": "react-select-3-option-0",
            },
            {
                "store_name": "Éxito San Mateo Cúcuta",
                "store_id": "react-select-3-option-1",
            },
        ],
    },
    "Ibagué": {
        "city_id": "react-select-2-option-18",
        "stores": [
            {"store_name": "Éxito Ibagué", "store_id": "react-select-3-option-0"}
        ],
    },
    "Manizales": {
        "city_id": "react-select-2-option-23",
        "stores": [
            {"store_name": "Éxito Manizales", "store_id": "react-select-3-option-0"}
        ],
    },
    "Montería": {
        "city_id": "react-select-2-option-25",
        "stores": [
            {
                "store_name": "Éxito Alamedas del Sinu",
                "store_id": "react-select-3-option-0",
            },
            {
                "store_name": "Éxito Montería Norte",
                "store_id": "react-select-3-option-1",
            },
        ],
    },
    "Pasto": {
        "city_id": "react-select-2-option-29",
        "stores": [
            {"store_name": "Éxito Pasto", "store_id": "react-select-3-option-0"}
        ],
    },
    "Pereira": {
        "city_id": "react-select-2-option-30",
        "stores": [
            {
                "store_name": "Éxito Parque Arboleda",
                "store_id": "react-select-3-option-0",
            },
            {"store_name": "Éxito Pereira Cuba", "store_id": "react-select-3-option-1"},
            {
                "store_name": "Éxito Pereira Victoria",
                "store_id": "react-select-3-option-2",
            },
        ],
    },
    "Villavicencio": {
        "city_id": "react-select-2-option-50",
        "stores": [
            {
                "store_name": "Éxito Sabana Villavicencio",
                "store_id": "react-select-3-option-0",
            },
            {
                "store_name": "Éxito Unicentro Villavicencio",
                "store_id": "react-select-3-option-1",
            },
        ],
    },
}


def should_scrape(product_info, city_name, store_name):
    # Create sanitized names for folders and check if file exists
    exito_name, sipsa_name = product_info
    safe_city_name = sanitize_filename(city_name)
    safe_store_name = sanitize_filename(store_name)
    json_file_path = os.path.join(
        "results", safe_city_name, safe_store_name, f"{sipsa_name}.json"
    )
    return not os.path.exists(json_file_path)


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


def clean_results_folder(sipsa_names):
    results_folder = "results"
    if not os.path.exists(results_folder):
        os.makedirs(results_folder, exist_ok=True)
        return

    # Traverse the directory structure: city/store/product.json
    for city_name in os.listdir(results_folder):
        city_path = os.path.join(results_folder, city_name)
        if not os.path.isdir(city_path):
            continue

        for store_name in os.listdir(city_path):
            store_path = os.path.join(city_path, store_name)
            if not os.path.isdir(store_path):
                continue

            for filename in os.listdir(store_path):
                if filename.endswith(".json"):
                    product_name = filename[:-5]
                    if product_name not in sipsa_names:
                        file_path = os.path.join(store_path, filename)
                        os.remove(file_path)
                        print(f"Deleted {file_path}")


def sanitize_filename(name):
    # Replace characters that might not be valid in filenames
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        name = name.replace(char, "_")
    return name


def scrape_product(product_info, city_name, city_id, store_name, store_id):
    exito_name, sipsa_name = product_info
    print(f"Getting {exito_name} from {store_name} in {city_name}...")

    # Create sanitized names for folders
    safe_city_name = sanitize_filename(city_name)
    safe_store_name = sanitize_filename(store_name)

    # Create directory structure
    city_folder = os.path.join("results", safe_city_name)
    os.makedirs(city_folder, exist_ok=True)

    store_folder = os.path.join(city_folder, safe_store_name)
    os.makedirs(store_folder, exist_ok=True)

    json_file_path = os.path.join(store_folder, f"{sipsa_name}.json")

    # Check if result already exists
    if os.path.exists(json_file_path):
        print(
            f"JSON file for {exito_name} at {store_name} in {city_name} already exists. Skipping scraping."
        )
        return

    # Execute scraping for this city, store, and product
    product = get_product(
        city={"city_name": city_name, "city_id": city_id},
        store={"store_name": store_name, "store_id": store_id},
        product_name=exito_name,
        sipsa_name=sipsa_name,
    )

    json.dump(
        product,
        open(json_file_path, "w", encoding="utf-8"),
        ensure_ascii=False,
        indent=4,
    )


if __name__ == "__main__":
    food_data = asyncio.run(get_food_data())

    products = [(food.exito_name, food.sipsa_name) for food in food_data]

    sipsa_names = {food.sipsa_name for food in food_data}

    clean_results_folder(sipsa_names)

    all_tasks = []
    skipped_tasks = 0
    for city_name, city_data in CITIES_AND_STORES.items():
        city_id = city_data["city_id"]
        for store in city_data["stores"]:
            for product_info in products:
                # Only add task if the file doesn't already exist
                if should_scrape(product_info, city_name, store["store_name"]):
                    all_tasks.append(
                        (
                            product_info,
                            city_name,
                            city_id,
                            store["store_name"],
                            store["store_id"],
                        )
                    )
                else:
                    skipped_tasks += 1

    print(f"Skipping {skipped_tasks} tasks that already have results")
    print(
        f"Preparing to scrape {len(all_tasks)} tasks across {len(CITIES_AND_STORES)} cities"
    )
    with ProcessPoolExecutor(max_workers=8) as executor:
        futures = [executor.submit(scrape_product, *task) for task in all_tasks]
        for future in futures:
            try:
                future.result()
            except Exception as e:
                print(f"Error during scraping: {e}")
