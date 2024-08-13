import os
import json
import argparse
from pathlib import Path
import asyncio
import signal
import requests
from fastapi import Request, HTTPException
from wallet.encryption.wallet import Wallet
from wallet.commands.comx_command_manager import ComxCommandManager, run_query_map_loop
from wallet.data_models import Settings

CONFIG = Settings()

manager = ComxCommandManager()

wallet = Wallet()

logger = CONFIG.loguru_logger
logger.info("Starting up api...")
logger.bind(name="api")

app = CONFIG.fastapi

templates = CONFIG.jinja2_templates

comx = CONFIG.communex_client


@app.on_event("startup")
async def startup_event():
    logger.info("Loading wallet...")
    wallet.init_keyring("wallet/keystore/key_dict")

    # Set up signal handlers for graceful shutdown
    for sig in (signal.SIGTERM, signal.SIGINT):
        signal.signal(sig, shutdown_handler)


def shutdown_handler(signum, frame):
    print(f"Received shutdown signal {signum}. Cleaning up...")
    # Clear keypairs and perform any other cleanup
    wallet.keyring.clear()
    # Stop the FastAPI app
    asyncio.get_event_loop().stop()


@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("main.html", {"request": request})


@app.get("/keys")
async def keys(request: Request):
    return templates.TemplateResponse("keys.html", {"request": request, "keys": wallet.keyring.keys()})


@app.get("/querymaps")
async def querymaps(request: Request):
    return templates.TemplateResponse("querymaps.html", {"request": request, "query_maps": manager.get_query_map_list()})


@app.get("/api/query_map/{map_name}")
async def get_query_map(map_name: str):
    if map_name not in manager.query_maps:
        raise HTTPException(status_code=404, detail="Query map not found")
    querymap_path = manager.querymap_path / f"{map_name}.json"
    return json.loads(querymap_path.read_text("utf-8"))


@app.get("api/key_details/{key}")
async def get_key_details(key: str):
    if key not in wallet.keyring:
        raise HTTPException(status_code=404, detail="Key not found")
    balance_path = manager.querymap_path / "balances.json"
    staketo_path = manager.querymap_path / "stake_to.json"
    stakefrom_path = manager.querymap_path / "stake_from.json"
    return {
        "ss58_address": wallet.keyring[key].ss58_address,
        "name": wallet.keyring[key].name,
        "balance": balance_path.read_text("utf-8")[key],
        "staketo": staketo_path.read_text("utf-8")[key],
        "stakefrom": stakefrom_path.read_text("utf-8")[key]
    }


@app.post("/api/transfer")
async def transfer(key: str, amount: float, dest: str):
    if key not in wallet.keyring:
        raise HTTPException(status_code=404, detail="Key not found")
    return comx.transfer(wallet.keyring[key], amount, dest)


@app.post("/api/transfer_stake")
async def transfer_stake(key: str, amount: float, from_key: str, dest: str):
    if key not in wallet.keyring:
        raise HTTPException(status_code=404, detail="Key not found")
    return comx.transfer_stake(wallet.keyring[key], amount, from_key, dest)


@app.post("/api/stake")
async def stake(key: str, amount: float, dest: str):
    if key not in wallet.keyring:
        raise HTTPException(status_code=404, detail="Key not found")
    return comx.stake(wallet.keyring[key], amount, dest)


@app.post("/api/unstake")
async def unstake(key: str, amount: float, dest: str): 
    if key not in wallet.keyring:
        raise HTTPException(status_code=404, detail="Key not found")
    return comx.unstake(wallet.keyring[key], amount, dest)

def get_exchange_rate():
    url = "https://api.comstats.org/stats/"
    stats_data = requests.get(url)
    if stats_data.status_code == 200:
        data = json.loads(stats_data.text)["stats"]
        return data["price"]
    

EXCHANGE_RATE = float(os.getenv('COM_TO_USD_RATE', get_exchange_rate())) 

@app.get("/reports")
async def reports(request: Request):
    report_types = ["balances", "staketo", "stakefrom"]
    return templates.TemplateResponse("reports.html", {
        "request": request, 
        "report_types": report_types
    })

@app.get("/api/report/{report_type}")
async def get_report(report_type: str):
    if report_type not in ["balances", "staketo", "stakefrom"]:
        raise HTTPException(status_code=404, detail="Report type not found")
    
    query_map_path = manager.querymap_path / f"{report_type}.json"
    if not query_map_path.exists():
        raise HTTPException(status_code=404, detail="Report data not found")
    
    report_data = json.loads(query_map_path.read_text("utf-8"))
    processed_data = None
    if report_type == "balance":
        # Extract only the free balance
        processed_data = {key: value['data']['free'] for key, value in report_data.items()}
    elif report_type in ["staketo", "stakefrom"]:
        # Sum up all stake amounts for each key
        processed_data = {key: sum(stake[1] for stake in value) for key, value in report_data.items()}
    
    return processed_data

def setup():
    CONFIG.port = input("Enter the port to listen on: ") or 5500

    CONFIG.host = input("Enter the host to listen on: ") or "0.0.0.0"
    
    CONFIG.reload = input("Enter the reload setting: ")
    
    CONFIG.querymap_path = Path(input("Enter the path to the query map: ")) or Path("static/query_maps")

    CONFIG.querymap_path.mkdir(parents=True, exist_ok=True)
    
def argument_parser():
    parser = argparse.ArgumentParser(description="Wallet API")
    parser.add_argument("--setup", action="store_true", help="Be prompted to enter the configuration of the wallet")
    parser.add_argument("--loop", action="store_true", help="Run the query map loop")

    return parser.parse_args()

# Run the FastAPI app
if __name__ == "__main__":
    args = argument_parser()
    if not os.path.exists("wallet/keystore/key_dict"):
        wallet.init_keydir()
    if args.setup:
        args.setup()
    if args.loop:
        asyncio.run(run_query_map_loop())
    else:
        import uvicorn
        uvicorn.run("wallet.api:app", host=CONFIG.host, port=CONFIG.port, reload=CONFIG.reload)