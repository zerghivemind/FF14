import requests
import json
import os
import time

os.chdir("C:\\Users\\domet\\Documents\\DA\\FF14")

# Set up API key and endpoint
xivapi_api_key = "87e529311ad84a0ca3e0c490bb1a7f6dc8c44ffdb375412abf8a72f522963afa"
recipe_url = "https://xivapi.com/recipe/{}"

recipes = []

# Load the recipe IDs from the JSON file
with open("recipes.json", "r") as f:
    recipe_ids = json.load(f).keys()

# Loop through each recipe and get the data
recipes = []
for recipe_id in recipe_ids:
    # Retrieve the recipe data from the API
    response = requests.get(
        recipe_url.format(recipe_id),
        params={
            "key": "87e529311ad84a0ca3e0c490bb1a7f6dc8c44ffdb375412abf8a72f522963afa"
        },
    )
    if response.status_code == 200:
        recipe = response.json()
        # Extract the recipe name and materials
        name = recipe["Name"]
        materials = []
        for key, value in recipe.items():
            if "AmountIngredient" in key and value > 0:
                index = int(key.split("Ingredient")[1])
                item_ingredient = recipe[f"ItemIngredient{index}"]
                materials.append(
                    {
                        "Amount": value,
                        "ID": item_ingredient["ID"],
                        "Name": item_ingredient["Name"],
                    }
                )
        recipes.append({"ID": recipe_id, "Name": name, "Materials": materials})
# Save the list of recipes to a JSON file
with open("recipes_with_materials.json", "w") as f:
    json.dump(recipes, f)
