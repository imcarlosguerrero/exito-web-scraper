from web_scraper import get_city_list, get_store_list, initialize_webdriver, get_product
from rich.progress import Progress, SpinnerColumn, TextColumn
from typing import Optional, List
from rich.console import Console
from rich.table import Table
from rich.text import Text
import unicodedata
import typer

app = typer.Typer(no_args_is_help=True)
# The driver can't be headless on Linux
console = Console()

def truncate_name(name, max_length=30):
    return name if len(name) <= max_length else name[:max_length] + "..."

def create_clickable_link(url):
    return Text("Click here", style="link " + url)

def normalize_input(user_input):
    user_input = user_input.strip()
    user_input = user_input.lower()
    user_input = unicodedata.normalize('NFKD', user_input)
    user_input = ''.join([c for c in user_input if not unicodedata.combining(c)])
    user_input = user_input.replace(' ', '-')
    
    return user_input

def parse_input(user_input):
    user_input = user_input.strip()
    user_input = user_input.lower()
    user_input = unicodedata.normalize('NFKD', user_input)
    user_input = ''.join([c for c in user_input if not unicodedata.combining(c)])
    user_input = user_input.replace('-', ' ')
    
    return user_input

def city_validator(driver, city: str):
    city_list = get_city_list(driver=driver)
    city_names = [city["city_name"] for city in city_list]
    
    found = False
    
    for index, city_name in enumerate(city_names):
        if normalize_input(city) in normalize_input(city_name):
            return city_list[index]

    if not found:
        raise typer.BadParameter(f"{city} was not found in the list of cities, please select one of the following: {city_names}")

def store_validator(driver, store: str, city: dict):
    store_list = get_store_list(driver=driver, city_id=city['city_id'])
    
    store_names = [store["store_name"] for store in store_list]
    
    found = False
    
    for index, store_name in enumerate(store_names):
        if normalize_input(store) in normalize_input(store_name):
            return store_list[index]
        
    if not found:
        raise typer.BadParameter(f"{store} was not found in the list of stores for {city['city_name']}, please select one of the following: {store_names}")

@app.command()
def list_cities():
    """
    Retrieves the list of cities available in the website.
    """
    driver = initialize_webdriver(headless=False)
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
        ) as progress:
            progress.add_task(description=f"Listing cities", total=None)
            
            city_list = get_city_list(driver=driver)
            
            table = Table(title="City List")
            
            table.add_column("City", justify="left", style="cyan", no_wrap=True)
            table.add_column("Store", justify="left", style="cyan", no_wrap=True)
            
            for index, city in enumerate(city_list):
                table.add_row(city["city_name"], str(index))

            console.print("\n", table)

@app.command()
def list_stores(cities: List[str] = typer.Argument(..., help="The name of the city to search for.")):
    """
    Retrieves the list of stores in a city.
    """
    driver = initialize_webdriver(headless=False)
    for city in cities:
        with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
        ) as progress:
            city = city_validator(driver, city)
            progress.add_task(description=f"Listing stores in {city['city_name']}", total=None)
            store_list = get_store_list(driver=driver, city_id=city['city_id'])
            
            table = Table(title="Store List")

            table.add_column("City", justify="left", style="cyan", no_wrap=True)
            table.add_column("Name", justify="left", style="cyan", no_wrap=True)
            table.add_column("ID", justify="left", style="cyan", no_wrap=True)

            for index, store in enumerate(store_list):
                table.add_row(city['city_name'], store["store_name"], str(index))

            console.print("\n", table)

@app.command()
def get_product_data(
    product: Optional[str] = typer.Argument("Huevo", help="The name of the product to search for."),
    store: Optional[str] = typer.Argument("Éxito Álamos", help="The name of the store to search in."),
    city: Optional[str] = typer.Argument("Bogotá", help="The name of the city to search in."),
):
    """
    Retrieves the price and discount of a product in a store in a city.
    """
    driver = initialize_webdriver(headless=False)
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        progress.add_task(description=f"Validating the input", total=None)
        city = city_validator(driver, city)
        store = store_validator(driver, store, city)
        product = parse_input(product)

    console.print(f"\nInput validation was successful.")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        progress.add_task(description=f"Looking results for {product} in {city['city_name']} at {store['store_name']}", total=None)
        products = get_product(driver=driver, city=city, store=store, product_name=product)

    table = Table(title="Product List")

    table.add_column("City", justify="left", style="cyan", no_wrap=True)
    table.add_column("Store", justify="left", style="cyan", no_wrap=True)
    table.add_column("URL", justify="left", style="cyan", no_wrap=True)
    table.add_column("Name", justify="left", style="cyan", no_wrap=True)
    table.add_column("Price", justify="left", style="cyan", no_wrap=True)
    table.add_column("Discount", justify="left", style="cyan", no_wrap=True)

    console.print(f"\nResults for {product} in {city['city_name']} at {store['store_name']} have been saved in the results folder")

    for product in products:
        table.add_row(
            product['city'],
            product['store'],
            create_clickable_link(product['url']),
            truncate_name(product['name'], 30),
            product['price'],
            str(product['discount']),
        )

    console.print("\n", table)

if __name__ == "__main__":
    app()