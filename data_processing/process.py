import pandas as pd

# Read the CSV file
df = pd.read_csv("datos_base.csv")

# Select only the columns we want to keep and rename them
columns_to_keep = ["City", "Codigo_TCAC", "Alimento"]
column_mapping = {"City": "city", "Codigo_TCAC": "tcac_code", "Alimento": "sipsa_name"}
df_filtered = df[columns_to_keep].rename(columns=column_mapping)

# Handle empty tcac_code values
# Replace empty strings, NaN and None with a default value
df_filtered["tcac_code"] = df_filtered["tcac_code"].fillna("N/A")
df_filtered.loc[df_filtered["tcac_code"].str.strip() == "", "tcac_code"] = "N/A"

# # Sort and drop duplicates, keeping all rows where tcac_code is "N/A"
# mask = df_filtered["tcac_code"] != "N/A"
# df_filtered.loc[mask] = (
#     df_filtered.loc[mask]
#     .sort_values(by=["city", "sipsa_name", "tcac_code"])
#     .drop_duplicates(subset=["city", "tcac_code"], keep="first")
# )

# Ensure no empty rows made it through
df_filtered = df_filtered[
    ~(
        (df_filtered["city"].isna() | (df_filtered["city"] == ""))
        & (
            df_filtered["tcac_code"].isna()
            | (df_filtered["tcac_code"] == "")
            | (df_filtered["tcac_code"] == "N/A")
        )
        & (df_filtered["sipsa_name"].isna() | (df_filtered["sipsa_name"] == ""))
    )
]

# Handle empty tcac_code values
# Replace empty strings, NaN and None with a default value
df_filtered["tcac_code"] = df_filtered["tcac_code"].fillna("N/A")
df_filtered.loc[df_filtered["tcac_code"].str.strip() == "", "tcac_code"] = "N/A"

# Clone sipsa_name column to create exito_name
df_filtered["exito_name"] = df_filtered["sipsa_name"]

# Define the mapping for renaming exito_name
rename_mapping = {
    "Arveja verde en vaina pastusa": "Arveja vaina",
    "Arveja verde seca importada": "Arveja",
    "Bagre rayado entero congelado": "Bagre",
    "Basa, entero congelado importado": "Basa",
    "Basa, filete congelado importado": "Filete basa",
    "Bocachico importado congelado": "Bocachico",
    "Calamar blanco entero": "Calamar",
    "Camarón tigre precocido seco": "Camarón tigre",
    "Carne de cerdo, brazo sin hueso": "Brazo cerdo",
    "Carne de cerdo, costilla": "Costila cerdo",
    "Carne de cerdo, lomo sin hueso": "Lomo cerdo",
    "Carne de cerdo, pernil sin hueso": "Pernil cerdo",
    "Carne de cerdo, tocino papada": "Papada cerdo",
    "Carne de res, bola de brazo": "Bola brazo res",
    "Carne de res, bola de pierna": "Bola pierna res",
    "Carne de res, cadera": "Cadera res",
    "Carne de res, chatas": "Chatas res",
    "Carne de res, costilla": "Costilla res",
    "Carne de res, falda": "Falda res",
    "Carne de res, morrillo": "Morrillo res",
    "Carne de res, muchacho": "Muchacho res",
    "Carne de res, pecho": "Pechho res",
    "Carne de res, punta de anca": "Punta de anca res",
    "Carne de res, sobrebarriga": "Sobrebarriga res",
    "Cebolla junca Aquitania": "Cebolla junca",
    "Corvina, filete congelado nacional": "Filete corvina",
    "Fríjol verde cargamanto": "Fríjol verde",
    "Huevo blanco A": "Huevo A",
    "Huevo blanco AA": "Huevo AA",
    "Huevo blanco AAA": "Huevo AAA",
    "Huevo rojo A": "Huevo A",
    "Huevo rojo AA": "Huevo AA",
    "Huevo rojo AAA": "Huevo AAA",
    "Huevo rojo extra": "Huevo AAA",
    "Jugo instantáneo (sobre)": "Refesco en polvo",
    "Langostino 16-20": "Langostino",
    "Mango común": "Mango",
    "Papa criolla limpia": "Papa criolla lavada",
    "Pargo rojo entero congelado": "Pargo",
    "Patilla": "Sandía",
    "Plátano hartón verde": "Plátano verde",
    "Pollo entero congelado sin vísceras": "Pollo entero sin vísceras",
    "Salmón, filete congelado": "Filete salmón",
    "Sierra entera congelada": "Sierra",
    "Tilapia roja entera congelada": "Tilapia",
    "Yuca ICA": "Yuca",
    "Yuca chirosa": "Yuca",
    "Ñame diamante": "Ñame",
    "Ñame criollo": "Ñame",
    "Ñame espino": "Ñame",
    "Limón común Ciénaga": "Limón común",
    "Fríjol verde bolo": "Fríjol verde",
    "Plátano dominico hartón maduro": "Plátano maduro",
    "Mojarra lora entera fresca": "Mojarra",
    "Mojarra lora entera congelada": "Mojarra",
    "Fríjol cargamanto blanco": "Fríjol blanco",
    "Plátano hartón verde Eje Cafetero": "Plátano verde",
    "Naranja común": "Naranja",
    "Ají topito dulce": "Ají topito",
    "Trucha entera fresca": "Trucha",
    "Cebollín chino": "Cebollín",
    "Cebolla junca Berlín": "Cebolla junca",
    "Papa Puracé": "Papa",
    "Mandarina común": "Mandarina",
    "Yuca criolla": "Yuca",
    "Rabadillas de pollo": "Rabadilla pollo",
    "Color (bolsita)": "Color",
    "Panela cuadrada blanca": "Panela cuadrada",
    "Fríjol verde en vaina": "Fríjol verde",
    "Cebolla cabezona roja peruana": "Cebolla cabezona roja",
    "Tomate Riogrande bumangués": "Tomate ",
    "Maracuyá valluno": "Maracuyá",
    "Plátano dominico hartón verde": "Plátano verde",
    "Fríjol cabeza negra importado": "Fríjol cabeza negra",
    "Cebolla cabezona blanca pastusa": "Cebolla cabezona blanca",
    "Blanquillo entero fresco": "Blanquillo",
    "Papa única": "Papa",
    "Plátano hartón verde ecuatoriano": "Plátano verde",
    "Tomate riñón": "Tomate",
    "Guayaba pera valluna": "Guayaba pera",
    "Maracuyá antioqueño": "Maracuyá",
    "Fríjol Zaragoza": "Fríjol",
    "Mandarina Oneco": "Mandarina",
    "Tomate riñón valluno": "Tomate chonto",
    "Remolacha regional": "Remolacha",
    "Cebolla junca pastusa": "Cebolla junca",
    "Guayaba común": "Guayaba",
    "Carne de cerdo, tocineta plancha": "Cerdo tocineta",
    "Fríjol Uribe rosado": "Fríjol",
    "Fríjol palomito importado": "Fríjol palomito",
    "Papa nevada": "Papa",
    "Manzana royal gala importada": "Manzana royal",
    "Papa Morasurco": "Papa",
    "Arracacha blanca": "Arracacha",
    "Fríjol cabeza negra nacional": "Fríjol cabeza negra",
    "Guayaba Atlántico": "Guayaba",
    "Plátano dominico verde": "Plátano verde",
    "Cebolla cabezona roja ocañera": "Cebolla cabezona roja",
    "Zanahoria bogotana": "Zanahoria",
    "Repollo blanco bogotano": "Repollo",
    "Cebolla cabezona blanca bogotana": "Cebolla cabezona blanca",
    "Remolacha bogotana": "Remolacha",
    "Carne de cerdo, brazo con hueso": "Cerdo brazo",
    "Carne de cerdo, lomo con hueso": "Cerdo lomo",
    "Carne de cerdo, pernil con hueso": "Cerdo pernil",
    "Carne de cerdo, tocino barriga": "Cerdo tocino",
    "Carne de cerdo, cabeza de lomo": "Cerdo lomo",
    "Carne de res, botas": "Res botas",
    "Carne de res, bota": "Res bota",
    "Carne de res, centro de pierna": "Res pierna",
    "Carne de res, lomo fino": "Res lomo",
    "Carne de res, lomo de brazo": "Res brazo",
    "Carne de res, murillo": "Res murillo",
    "Carne de res, paletero": "Res paletero",
    "Plátano hartón verde llanero": "Plátano verde",
    "Plátano hartón maduro": "Plátano maduro",
}

# Apply the mapping to exito_name
df_filtered["exito_name"] = df_filtered["exito_name"].replace(rename_mapping)

# Find sipsa_names present in other cities but not in Bogotá
bogota_sipsa_names = set(df_filtered[df_filtered["city"] == "Bogotá"]["sipsa_name"])
other_cities_sipsa_names = set(
    df_filtered[df_filtered["city"] != "Bogotá"]["sipsa_name"]
)


# Get the difference
unique_to_other_cities = other_cities_sipsa_names - bogota_sipsa_names

# Print the result
print("sipsa_names present in other cities but not in Bogotá:")
print(unique_to_other_cities)
print(len(unique_to_other_cities))

# Find tcac_codes present in other cities but not in Bogotá
bogota_tcac_codes = set(df_filtered[df_filtered["city"] == "Bogotá"]["tcac_code"])
other_cities_tcac_codes = set(df_filtered[df_filtered["city"] != "Bogotá"]["tcac_code"])

# Get the difference
unique_tcac_codes_to_other_cities = other_cities_tcac_codes - bogota_tcac_codes

# Print the result
print("\ntcac_codes present in other cities but not in Bogotá:")
print(unique_tcac_codes_to_other_cities)
print(len(unique_tcac_codes_to_other_cities))

# Generate a DataFrame with only the items in Bogotá
df_bogota = df_filtered[df_filtered["city"] == "Bogotá"]

# Save the filtered dataframe to a new CSV file
df_filtered.to_csv("processed_data.csv", index=False)

# Save the Bogotá-specific dataframe to another CSV file
df_bogota.to_csv("processed_bogota_data.csv", index=False)
