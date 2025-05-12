import os, json
from db_operations import store_partnership_data, fetch_partnership_data

data_file = os.path.abspath(os.path.join(__file__, "../../../data/faro/data.json"))

with open(data_file, 'r') as file:
    data = json.load(file)

# print(data)
# store_partnership_data(data)

fetched_data = fetch_partnership_data("faro")
print(fetched_data)