import requests
import json
import os
import time
import psycopg2
from tqdm import tqdm

os.chdir("C:\\Users\\domet\\Documents\\DA\\FF14")

conn = psycopg2.connect(
    host="localhost",
    database="postgres",
    user="postgres",
    password="123456",
    port="5432",
)
cur = conn.cursor()

cur.execute("SELECT name, id FROM datacenters")
dc = cur.fetchall()

with open("material_ids.json", "r") as f:
    material_ids = json.load(f)

for row in dc:
    datacenter_name = row[0]
    datacenter_id = row[1]

    if datacenter_name != "Aether":
        continue

    for material_id in tqdm(
        material_ids, desc=f"Processing material IDs for {datacenter_name}"
    ):
        url = f"https://universalis.app/api/{datacenter_name}/{material_id}"
        params = {"entries": 100}

        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            time.sleep(1)
            for listing in data["listings"]:
                world_name = listing["worldName"]
                server_name = world_name.replace(" ", "").capitalize()
                price = listing["pricePerUnit"]
                quantity = listing["quantity"]
                hq = listing["hq"]
                cur.execute("SELECT id FROM servers WHERE name=%s", (server_name,))
                server_row = cur.fetchone()
                if server_row is not None:
                    server_id = server_row[0]
                    # Check if the entry already exists in the database
                    cur.execute(
                        "SELECT id FROM datacenter_items WHERE datacenter_id=%s AND server_id=%s AND material_id=%s",
                        (datacenter_id, server_id, material_id),
                    )
                    existing_row = cur.fetchone()
                    if existing_row is not None:
                        # Update the existing entry
                        cur.execute(
                            "UPDATE datacenter_items SET price=%s, quantity=%s, hq=%s WHERE id=%s",
                            (price, quantity, hq, existing_row[0]),
                        )
                    else:
                        # Insert a new entry
                        cur.execute(
                            "INSERT INTO datacenter_items (datacenter_id, server_id, material_id, price, quantity, hq) VALUES (%s, %s, %s, %s, %s, %s)",
                            (datacenter_id, server_id, material_id, price, quantity, hq),
                        )
                    # Commit the changes for the current server
                    conn.commit()
                else:
                    print(f"Server {server_name} not found in database.")

            # Check if we have processed all material_ids, and exit the loop if we have
            if material_id == material_ids[-1]:
                break
