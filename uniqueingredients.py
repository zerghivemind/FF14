import requests
import json
import os
import time

os.chdir("C:\\Users\\domet\\Documents\\DA\\FF14")

with open("recipes_with_materials.json", "r") as f:
    data = json.load(f)

material_ids = []

for recipe in data:
    materials = recipe["Materials"]
    for material in materials:
        material_id = material["ID"]
        material_ids.append(material_id)

# Get unique material IDs
unique_material_ids = list(set(material_ids))

# Save the list of unique material IDs to a JSON file
with open("material_ids.json", "w") as f:
    json.dump(unique_material_ids, f)