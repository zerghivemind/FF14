import requests
import json
import os
import time
import psycopg2
from tqdm import tqdm

os.chdir("C:\\Users\\domet\\Documents\\DA\\FF14")

# /api/v2/{worldDcRegion}/{itemIds}
#############################################
# if response.status_code == 200:
#     item_data = response.json()
#     with open('item_data.json', 'w') as f:
#         json.dump(item_data, f)

# with open('item_data.json', 'r') as f:
#     item = json.load(f)

# for listing in item['listings']:
#     price = listing['pricePerUnit']
#     quantity = listing['quantity']
#     datacenter = listing['worldName']
#     hq = listing['hq']
#     print(f"Price per unit: {price}, Quantity: {quantity}, Datacenter: {datacenter}, HQ: {hq}")
#     print(len(item['listings']))
#############################################
# conn = psycopg2.connect(
#     host="localhost",
#     database="postgres",
#     user="postgres",
#     password="123456",
#     port="5432"
# )
# cur = conn.cursor()

# cur.execute("SELECT name, id FROM datacenters")
# dc = cur.fetchall()

# cur.execute("""CREATE TABLE datacenter_items (
#                 id SERIAL PRIMARY KEY,
#                 datacenter_id INTEGER NOT NULL REFERENCES datacenters(id),
#                 server_id INTEGER NOT NULL REFERENCES servers(id),
#                 material_id INTEGER NOT NULL REFERENCES recipe_materials(id),
#                 price INTEGER NOT NULL,
#                 quantity INTEGER NOT NULL,
#                 hq BOOLEAN NOT NULL,
#                 CONSTRAINT fk_datacenter FOREIGN KEY (datacenter_id) REFERENCES datacenters(id),
#                 CONSTRAINT fk_server FOREIGN KEY (server_id) REFERENCES servers(id),
#                 CONSTRAINT fk_material FOREIGN KEY (material_id) REFERENCES recipe_materials(id)

#             )""")

# with open('material_ids.json', 'r') as f:
#     material_ids = json.load(f)

# for row in dc:
#     datacenter_name = row[0]
#     datacenter_id = row[1]

#     if datacenter_name != "Aether":
#         continue

#     for material_id in tqdm(material_ids, desc=f"Processing material IDs for {datacenter_name}"):
#         url = f"https://universalis.app/api/{datacenter_name}/{material_id}"
#         params = {"entries": 100}

#         response = requests.get(url, params=params)
#         if response.status_code == 200:
#             data = response.json()
#             time.sleep(1)
#             for listing in data['listings']:
#                 world_name = listing['worldName']
#                 server_name = world_name.replace(' ', '').capitalize()
#                 price = listing['pricePerUnit']
#                 quantity = listing['quantity']
#                 hq = listing['hq']
#                 cur.execute("SELECT id FROM servers WHERE name=%s", (server_name,))
#                 server_row = cur.fetchone()
#                 if server_row is not None:
#                     server_id = server_row[0]
#                     # Insert the data into the database
#                     cur.execute("INSERT INTO datacenter_items (datacenter_id, server_id, material_id, price, quantity, hq) VALUES (%s, %s, %s, %s, %s, %s)", (datacenter_id, server_id, material_id, price, quantity, hq))
#                     # Commit the changes for the current server
#                     conn.commit()
#                 else:
#                     print(f"Server {server_name} not found in database.")

#                 cur.execute("SELECT id FROM servers WHERE name=%s", (server_name,))
#                 server_row = cur.fetchone()
#                 if server_row is not None:
#                     server_id = server_row[0]
#                     # Insert the data into the database
#                     cur.execute("INSERT INTO datacenter_items (datacenter_id, server_id, material_id, price, quantity, hq) VALUES (%s, %s, %s, %s, %s, %s)", (datacenter_id, server_id, material_id, price, quantity, hq))
#                     # Commit the changes for the current server
#                     conn.commit()
#                 else:
#                     print(f"Server {server_name} not found in database.")
#                     #print(f"Price per unit: {price}, Quantity: {quantity}, Datacenter: {datacenter_name}, Server ID: {server_id}, HQ: {hq}")

#             # Check if we have processed all material_ids, and exit the loop if we have
#             if material_id == material_ids[-1]:
#                 break
#############################################
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

# /api/v2/{worldDcRegion}/{itemIds}
# cur.execute(""" CREATE TABLE server_recipe(
#                 id SERIAL PRIMARY KEY,
#                 server_id INTEGER NOT NULL REFERENCES servers(id),
#                 recipe_id INTEGER NOT NULL REFERENCES recipes(id),
#                 price INTEGER NOT NULL,
#                 quantity INTEGER NOT NULL,
#                 hq BOOLEAN NOT NULL

# )
# """)
try:
    with open("state.json", "r") as state_file:
        state = json.load(state_file)
except FileNotFoundError:
    state = {
        "datacenter_name": None,
        "last_processed_server": None
    }
target_datacenter = "Aether"  # Specify the target datacenter here

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