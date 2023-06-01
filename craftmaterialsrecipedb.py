import requests
import json
import os
import time
import psycopg2

os.chdir("C:\\Users\\domet\\Documents\\DA\\FF14")

# with open('recipes.json', 'r') as f:
#     recipes = json.load(f)

# conn = psycopg2.connect(
#     host="localhost",
#     database="postgres",
#     user="postgres",
#     password="123456",
#     port="5432"
# )
# cur = conn.cursor()

# cur.execute("""
#     CREATE TABLE recipes (
#         id INTEGER PRIMARY KEY,
#         name VARCHAR(255) NOT NULL
#     );
# """)

# for recipe_id, recipe in recipes.items():
#     if not recipe['name']:
#         continue
#     cur.execute("INSERT INTO recipes (id, name) VALUES (%s, %s)", (int(recipe_id), recipe['name']))

# conn.commit()
# cur.close()
# conn.close()

###############################################################################

with open("recipes_with_materials.json", "r") as f:
    recipes = json.load(f)

conn = psycopg2.connect(
    host="localhost",
    database="postgres",
    user="postgres",
    password="123456",
    port="5432",
)
cur = conn.cursor()
cur.execute(
    """CREATE TABLE recipe_materials (
    id SERIAL PRIMARY KEY,
    recipe_id VARCHAR(10) NOT NULL,
    recipe_name VARCHAR(100),
    material_id VARCHAR(10) NOT NULL,
    material_name VARCHAR(100) NOT NULL,
    material_amount INTEGER NOT NULL
);"""
)

for recipe in recipes:
    recipe_id = recipe["ID"]
    recipe_name = (
        recipe["Name"] if "Name" in recipe and recipe["Name"] is not None else None
    )
    materials = recipe["Materials"]
    if not recipe_name:
        continue  # Skip this recipe if the name is missing
    for material in materials:
        count = 0
        material_id = material[
            "ID"
        ]  # Assuming the material IDs are stored in the 'ID' field of the material object
        material_name = material["Name"]
        material_amount = material["Amount"]
        cur.execute(
            "INSERT INTO recipe_materials (recipe_id, recipe_name, material_id, material_name, material_amount) VALUES (%s, %s, %s, %s, %s)",
            (recipe_id, recipe_name, material_id, material_name, material_amount),
        )
        conn.commit()
conn.close()

###############################################################################
