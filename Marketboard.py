import requests
import json
import os
import time

os.chdir("C:\\Users\\domet\\Documents\\DA\\FF14")


item_data_dict = {}
# XIVAPI API key
xivapi_api_key = "87e529311ad84a0ca3e0c490bb1a7f6dc8c44ffdb375412abf8a72f522963afa"

# Get list of marketable items
marketable_items = requests.get("https://universalis.app/api/v2/marketable")
json_data = json.loads(marketable_items.text)

# Initialize dictionary to hold item data
item_data_dict = {}

# Check each item in the list
for item_id in json_data:
    while True:
        try:
            # Request data from XIVAPI
            response = requests.get(
                f"https://xivapi.com/item/{item_id}?private_key={xivapi_api_key}"
            )
            if response.status_code == 200:
                # If request is successful, add item name to dictionary
                item_data = response.json()
                item_data_dict[item_id] = item_data["Name"]
                print(f"Added item ID {item_id} to dictionary")
                break  # Break out of loop if request is successful
            else:
                # If request is not successful, print error message and wait before retrying
                print(
                    f"Response code {response.status_code} for item ID {item_id}, retrying in 5 seconds..."
                )
                time.sleep(5)
        except:
            # If request fails, print error message and wait before retrying
            print(f"Request failed for item ID {item_id}, retrying in 5 seconds...")
            time.sleep(5)

    # Write dictionary to file after each item is processed
    try:
        with open("marketboard.json", "w") as outfile:
            json.dump(item_data_dict, outfile)
            print("Data written to file")
    except:
        print("Error writing data to file")
