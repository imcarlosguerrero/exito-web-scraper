from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from models.food import Food
import asyncio
from pymongo.errors import DuplicateKeyError
import pandas as pd


async def initialize_motor():
    client = AsyncIOMotorClient("mongodb://localhost:27017")

    await init_beanie(
        database=client["foodprice"],
        document_models=[Food],
    )


async def delete_collection():
    try:
        await Food.delete_all()
        print("Successfully deleted all records from collection")
        return True
    except Exception as e:
        print(f"Error deleting collection: {str(e)}")
        return False


async def insert_food_data(processed_data):
    try:
        # Convert DataFrame rows to list of Food documents
        food_documents = []
        for _, row in processed_data.iterrows():
            print(row)
            if pd.isna(row["tcac_code"]) or row["tcac_code"] == "N/A":
                row["tcac_code"] = None

            food_doc = Food(
                city=row["city"],
                tcac_code=row["tcac_code"],
                sipsa_name=row["sipsa_name"],
                exito_name=row["exito_name"],
            )
            food_documents.append(food_doc)

        # Insert all documents
        try:
            await Food.insert_many(food_documents)
            print(f"Successfully inserted {len(food_documents)} records")
            return True
        except DuplicateKeyError:
            success_count = 0
            for doc in food_documents:
                try:
                    await doc.insert()
                    success_count += 1
                except DuplicateKeyError:
                    continue

            print(
                f"Inserted {success_count} records, skipped {len(food_documents) - success_count} duplicates"
            )
            return True

    except Exception as e:
        print(f"Error inserting data: {str(e)}")
        return False


async def main():
    await initialize_motor()
    processed_data = pd.read_csv("processed_data.csv")
    await delete_collection()
    await insert_food_data(processed_data)


if __name__ == "__main__":
    asyncio.run(main())
