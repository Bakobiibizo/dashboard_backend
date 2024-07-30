import json
import argparse
from pathlib import Path
import asyncio
import signal
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
    balance_path = manager.querymap_path / "query_map_balance.json"
    staketo_path = manager.querymap_path / "query_map_stake_to.json"
    stakefrom_path = manager.querymap_path / "query_map_stake_from.json"
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

def argument_parser():
    parser = argparse.ArgumentParser(description="Wallet API")
    parser.add_argument("--setup", action="store_true", help="Be prompted to enter the configuration of the wallet")
    parser.add_argument("--loop", action="store_true", help="Run the query map loop")

    return parser.parse_args()

def setup():
    CONFIG.port = input("Enter the port to listen on: ")

    CONFIG.host = input("Enter the host to listen on: ")
    
    CONFIG.reload = input("Enter the reload setting: ")
    
    CONFIG.keyring_path = Path(input("Enter the path to the keyring: "))
    
    CONFIG.keyring_path.mkdir(parents=True, exist_ok=True)
    
    CONFIG.querymap_path = Path(input("Enter the path to the query map: "))

    CONFIG.querymap_path.mkdir(parents=True, exist_ok=True)
    

# Run the FastAPI app
if __name__ == "__main__":
    args = argument_parser()
    if args.setup:
        args.setup()
    if args.loop:
        asyncio.run(run_query_map_loop())
    else:
        import uvicorn
        uvicorn.run("wallet.api:app", host=CONFIG.host, port=CONFIG.port, reload=CONFIG.reload)