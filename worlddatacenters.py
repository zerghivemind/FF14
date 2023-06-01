import requests
import json
import os
import time
import psycopg2

os.chdir("C:\\Users\\domet\\Documents\\DA\\FF14")

xivapi_api_key = "87e529311ad84a0ca3e0c490bb1a7f6dc8c44ffdb375412abf8a72f522963afa"
url = "https://xivapi.com/servers"

# params = {
#     "language": "en"
# }

# response = requests.get(url, params=params, )
# if response.status_code == 200:
#     servers = response.json()
#     print(servers)

# datacenter_url = "https://xivapi.com/servers/dc"
# # Retrieve the datacenter data from the API
# response = requests.get(datacenter_url, params={'key': xivapi_api_key})
# if response.status_code == 200:
#     datacenters = response.json()
#     datacenters_dict = {}
#     for datacenter, servers in datacenters.items():
#         datacenters_dict[datacenter] = servers
#     json_string = json.dumps(datacenters_dict)

#     with open('datacenter_dict.json', 'r') as f:
#         json.dump(datacenters_dict, f)
###############################################################################

# with open('datacenter_dict.json', 'r') as f:
#     datacenters = json.load(f)

# # create a connection to the PostgreSQL server
# conn = psycopg2.connect(
#     host="localhost",
#     database="postgres",
#     user="postgres",
#     password="123456",
#     port="5432"
# )


# cur = conn.cursor()
# datacenter_lists = []

# cur.execute("""CREATE TABLE datacenters (
#     id SERIAL PRIMARY KEY,
#     name VARCHAR(50) UNIQUE NOT NULL
#     )""")

# for datacenter, servers in datacenters.items():
#     cur.execute("INSERT INTO datacenters (name) VALUES (%s)", (datacenter,))

# conn.commit()
# cur.close()
# conn.close()

###############################################################################

with open("datacenter_dict.json", "r") as f:
    datacenters = json.load(f)
conn = psycopg2.connect(
    host="localhost",
    database="postgres",
    user="postgres",
    password="123456",
    port="5432",
)
cur = conn.cursor()
cur.execute(
    """CREATE TABLE servers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    datacenter_id INTEGER REFERENCES datacenters(id)
);"""
)


datacenter_ids = {}
for datacenter, servers in datacenters.items():
    cur.execute("SELECT id FROM datacenters WHERE name = %s", (datacenter,))
    datacenter_id = cur.fetchone()[0]
    datacenter_ids[datacenter] = datacenter_id

    for server in servers:
        cur.execute(
            "INSERT INTO servers (name, datacenter_id) VALUES (%s, %s)",
            (server, datacenter_id),
        )

# Commit the changes and close the cursor and connection
conn.commit()
cur.close()
conn.close()
