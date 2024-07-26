from loguru import logger

from generate.get_all_balance import check_keyring
from generate.query_maps import REPORT_MAP

def process_data(report_selection):
    logger.info("process_data")
    check_keyring(REPORT_MAP[report_selection])
    with open("main_reports/keyring.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    return data

def generate_json_object(data):
    new_dict = []
    for _, value in data.items():
        new_dict.append(value)
    return new_dict

def generate_markdown_table(data):
    # Define the headers
    headers = ["Key", "Name", "Balance", "Stake", "Total", "Stake From"]
    
    # Start the table with headers
    table = "| " + " | ".join(headers) + " |\n"
    table += "|" + "|".join(["---" for _ in headers]) + "|\n"
    
    # Add each row
    for key, value in data.items():
        row = [
            #key[:10] + "...",  # Truncate the key for readability
            value['name'],
            str(value['balance']),
            str(value['stake']),
            str(value['total']),
            str(value['stake_from'])
        ]
        table += "| " + " | ".join(row) + " |\n"
    
    return table