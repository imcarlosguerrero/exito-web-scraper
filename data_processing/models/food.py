from beanie import Document
from typing import Optional


class Food(Document):
    sipsa_name: str
    exito_name: str
    tcac_code: Optional[str] = None

    class Settings:
        name = "food_names"
