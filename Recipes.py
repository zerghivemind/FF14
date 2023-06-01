import requests
import json
import os
import time

os.chdir("C:\\Users\\domet\\Documents\\DA\\FF14")

# Set up API key and endpoint
xivapi_api_key = "87e529311ad84a0ca3e0c490bb1a7f6dc8c44ffdb375412abf8a72f522963afa"
url = "https://xivapi.com/recipe"

params = {
    "key": "87e529311ad84a0ca3e0c490bb1a7f6dc8c44ffdb375412abf8a72f522963afa",
    "page": 1,
    "columns": "ID,Name",
}

response_text_list = []
recipes = {}

while True:
    response = requests.get(url, params=params)
    data = response.json()
    for recipe in data["Results"]:
        recipes[recipe["ID"]] = {"name": recipe["Name"]}

    response_text_list.append(data)
    if len(data["Results"]) < params.get("limit", 100):
        break
    params["page"] += 1

with open("recipes.json", "a") as f:
    json.dump(recipes, f)
