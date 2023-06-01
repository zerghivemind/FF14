import requests
import json
import os
import time
import psycopg2
from tqdm import tqdm

os.chdir("C:\\Users\\domet\\Documents\\DA\\FF14")

try:
    with open("state.json", "r") as state_file:
        state = json.load(state_file)
except FileNotFoundError:
    state = {
        "datacenter_name": None,
        "last_processed_server": None
    }
with open("datacenter_dict.json", "r") as f:
    dcwithservers = json.load(f)
with open("recipes.json", "r") as f:
    recipes = json.load(f)
recipe_ids = recipes.keys()

conn = psycopg2.connect(
    host="localhost",
    database="postgres",
    user="postgres",
    password="123456",
    port="5432",
)
cur = conn.cursor()
target_datacenter = "Crystal"  # Specify the target datacenter here

datacenter_processed = False

for datacenter_name, servers in dcwithservers.items():
    if datacenter_name != target_datacenter:
        continue
    datacenter_processed = True
    for server in servers:
        
        last_processed_server = server
        server_name = server.replace(" ", "").capitalize()
        cur.execute("SELECT id FROM servers WHERE name=%s", (server_name,))
        server_row = cur.fetchone()
        if server_row is None:
            print(f"Skipping {server_name} because it is not in the database.")
            continue
        server_id = server_row[0]
        state["datacenter_name"] = datacenter_name
        state["last_processed_server"] = server
        with open("state.json", "w") as state_file:
            json.dump(state, state_file)
        for recipe_id in tqdm(
            recipe_ids, desc=f"Server {server}", total=len(recipe_ids)
        ):
            
            url = f"https://universalis.app/api/{server}/{recipe_id}"
            params = {"entries": 100}
            response = requests.get(url, params=params)
            time.sleep(1)
            if response.status_code == 200:
                recipe_data = response.json()
                server_name = server.replace(" ", "").capitalize()
                # print(f"server_name: {server_name}")
                cur.execute("SELECT id FROM servers WHERE name=%s", (server_name,))
                server_row = cur.fetchone()
                # print(f"server_row: {server_row}")
                if server_row is not None:
                    server_id = server_row[0]
                    if recipe_data.get("listings") is None:
                        print(
                            f"No listings found for recipe {recipe_id} on server {server_name}"
                        )
                        continue
                    for listing in recipe_data["listings"]:
                        price = listing["pricePerUnit"]
                        quantity = listing["quantity"]
                        hq = listing["hq"]
                        # Check if the recipe exists before inserting into the server_items table
                        cur.execute("SELECT id FROM recipes WHERE id=%s", (recipe_id,))
                        recipe_row = cur.fetchone()
                        if recipe_row is None:
                            print(
                                f"Skipping recipe {recipe_id} on server {server_name} because it does not exist."
                            )
                            continue
                        # Insert the data into the database
                        cur.execute(
                            "INSERT INTO server_recipe (server_id, recipe_id, price, quantity, hq) VALUES (%s, %s, %s, %s, %s)",
                            (server_id, recipe_id, price, quantity, hq),
                        )
                        # Commit the changes for the current listing
                        conn.commit()
                else:
                    print(f"No rows found in servers table for {server_name}")
                state["datacenter_name"] = datacenter_name
                state["last_processed_server"] = None
                state["last_processed_recipe"] = recipe_id
                with open("state.json", "w") as state_file:
                    json.dump(state, state_file)