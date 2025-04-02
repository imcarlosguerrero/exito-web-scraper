import pandas as pd
import json
from typing import List, Dict, Any, Optional


class Food:
    def __init__(
        self, city: str, tcac_code: Optional[str], sipsa_name: str, exito_name: str
    ):
        self.city = city
        self.tcac_code = tcac_code
        self.sipsa_name = sipsa_name
        self.exito_name = exito_name

    def to_dict(self) -> Dict[str, Any]:
        return {
            "city": self.city,
            "tcac_code": self.tcac_code,
            "sipsa_name": self.sipsa_name,
            "exito_name": self.exito_name,
        }


def export_foods_to_json(foods: List[Food], filename="foods.json") -> bool:
    try:
        # Convert Food objects to dictionaries
        food_dicts = [food.to_dict() for food in foods]

        # Write to JSON file
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(food_dicts, f, indent=2, ensure_ascii=False)

        print(f"Successfully exported {len(food_dicts)} food records to {filename}")
        return True
    except Exception as e:
        print(f"Error exporting data to JSON: {str(e)}")
        return False


def process_food_data(processed_data: pd.DataFrame) -> List[Food]:
    try:
        food_objects = []
        for _, row in processed_data.iterrows():
            print(row)
            if pd.isna(row["tcac_code"]) or row["tcac_code"] == "N/A":
                row["tcac_code"] = None

            food_obj = Food(
                city=row["city"],
                tcac_code=row["tcac_code"],
                sipsa_name=row["sipsa_name"],
                exito_name=row["exito_name"],
            )
            food_objects.append(food_obj)

        print(f"Successfully processed {len(food_objects)} records")
        return food_objects

    except Exception as e:
        print(f"Error processing data: {str(e)}")
        return []


def main():
    try:
        processed_data = pd.read_csv("processed_data.csv")
        food_objects = process_food_data(processed_data)
        export_foods_to_json(food_objects, "foods.json")
        print("Data processing completed successfully")
    except Exception as e:
        print(f"Error in main process: {str(e)}")


if __name__ == "__main__":
    main()
