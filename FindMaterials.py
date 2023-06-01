import requests
import json
import os
import time

os.chdir("C:\\Users\\domet\\Documents\\DA\\FF14")
# read json file
with open("Bronze Ingot.json", "r") as f:
    data = json.load(f)

for key, value in data.items():
    if "AmountIngredient" in key and value > 0:
        index = int(key.split("Ingredient")[1])
        item_ingredient = data[f"ItemIngredient{index}"]
        item_id = item_ingredient["ID"]
        for item_key, item_value in item_ingredient.items():
            print(f"Amount: {value}, Item: {item_ingredient['Name']}, ID: {item_id}")
            break
