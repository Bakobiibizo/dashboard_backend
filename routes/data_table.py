import json
import http
from fastapi import APIRouter, Request, HTTPException
from fastapi.templating import Jinja2Templates
from generate.get_all_balance import get_balances, check_keyring
from loguru import logger


router = APIRouter()
templates = Jinja2Templates(directory="component_library/templates")


@router.get("/data-table")
async def data_table(request: Request):
    logger.info("Loading data table...")
    data = get_data(request)
    return templates.TemplateResponse(
        "components/data_table.html", {"request": request, "data": data}
    )


REPORT_MAP = {
    "eden": "main_reports/eden.json",
    "personal": "main_reports/personal.json",
    "staff": "main_reports/staff.json",
    "huck": "main_reports/huck.json",
}


def get_data(reportSelection: str = "eden"):
    logger.info("Loading data...")
    report_path = REPORT_MAP[reportSelection]
    check_keyring(report_path)
    with open("main_reports/keyring.json", "r", encoding="utf-8") as f:
        json_data = f.read()
    data_dict = json.loads(json_data)
    try:
        return get_balances(data_dict)
    except HTTPException as e:
        logger.error(f"Error loading data: {e}\n{data_dict}")
        raise HTTPException(
            {"status_code": 500, "message": "Error loading data"}
        ) from e
