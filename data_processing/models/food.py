from typing import Optional
from pydantic import BaseModel


class Food(BaseModel):
    sipsa_name: str
    exito_name: str
    tcac_code: Optional[str] = None
