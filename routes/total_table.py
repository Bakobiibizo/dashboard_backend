import json
import requests
from fastapi import Request
from generate.get_all_balance import check_keyring, get_all_balances
from fastapi.routing import APIRouter
from data_models import format_as_currency

URL = "https://n8n.zshare.us/webhook/c6f3ce61-a151-4e90-b52d-df00e7ff03ca"

router = APIRouter()


@router.get("/totals/{report_selection}")
def get_table_data(requests: Request, report_selection: str = "eden"):
    table_data = get_table_data(report_selection)
    post_data(table_data)


def post_data(table_data: dict):
    response = requests.post(URL, json=table_data, timeout=30)
    return json.loads(response.text) if response.status_code == 200 else None


def get_table_data(report_selection: str = "eden"):
    with open("main_reports/keyring.json", "r", encoding="utf-8") as f:
        table_data = json.loads(f.read())

    total_balance = 0
    total_staketo = 0
    grand_total = 0
    total_stakefrom = 0

    for _, value in table_data.items():
        total_balance += value["balance"]
        total_staketo += value["stake"]
        grand_total += value["total"]
        total_stakefrom += value["total"]

    return {
        "Total Stake From": format_as_currency(total_stakefrom),
        "Total Balance": format_as_currency(total_balance),
        "Total Stake": format_as_currency(total_staketo),
        "Grand Total": format_as_currency(grand_total),
    }


if __name__ == "__main__":
    table_data = {}
    table_data["Totals"] = get_table_data("eden")
    post_data(table_data)
