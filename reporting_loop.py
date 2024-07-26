import requests
from routes.total_table import get_table_data, post_data
from routes.data_table import get_data, 

while True:
    data = get_data()
    table_data = get_table_data()
    post_data(table_data)