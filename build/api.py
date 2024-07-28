import os
import json
from pathlib import Path
import asyncio
import signal

from data_models import (
    wallet,
    manager,
    app,
    templates,
    logger,
    Request
)

logger.info("Starting up api...")
logger.bind(name="api")

@app.on_event("startup")
async def startup_event():
    logger.info("Loading wallet...")
    wallet.keypairs = wallet.load_keys()

    # Set up signal handlers for graceful shutdown
    for sig in (signal.SIGTERM, signal.SIGINT):
        signal.signal(sig, shutdown_handler)

def shutdown_handler(signum, frame):
    print(f"Received shutdown signal {signum}. Cleaning up...")
    # Clear keypairs and perform any other cleanup
    wallet.keypairs.clear()
    # Stop the FastAPI app
    asyncio.get_event_loop().stop()

@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("main.html", {"request": request})

@app.get("/keys")
async def keys(request: Request):
    return templates.TemplateResponse("keys.html", {"request": request, "keys": manager.get_key_data()})

@app.get("/querymaps")
async def querymaps(request: Request):
    return templates.TemplateResponse("querymaps.html", {"request": request, "query_maps": manager.})

@app.get("/api/query_map/{map_name}")
async def get_query_map(map_name: str):
    if map_name not in QUERY_MAP:
        raise HTTPException(status_code=404, detail="Query map not found")
    querymap_path = Path("./query_maps/query_map_{map_name}.json")
    return json.loads(querymap_path.read_text("utf-8"))

@app.get("api/key_details/{key}")
async def get_key_details(key: str):
    if key not in keypairs:
        raise HTTPException(status_code=404, detail="Key not found")
    key_data = key_data = {
        "ss58_address": keypairs[key].ss58_address,
        "name": keypairs[key].name,
        "balance": 
        "staketo":
    }

@app.post("/api/transfer")
async def transfer(key: str, amount: float, dest: str):
    if key not in keypairs:
        raise HTTPException(status_code=404, detail="Key not found")
    return comx.transfer(keypairs[key], amount, dest)

@app.post("/api/transfer_stake")
async def transfer_stake(key: str, amount: float, from_key: str, dest: str):
    if key not in keypairs:
        raise HTTPException(status_code=404, detail="Key not found")
    return comx.transfer_stake(keypairs[key], amount, from_key, dest)

@app.post("/api/stake")
async def stake(key: str, amount: float, dest: str):
    if key not in keypairs:
        raise HTTPException(status_code=404, detail="Key not found")
    return comx.stake(keypairs[key], amount, dest)

@app.post("/api/unstake")
async def unstake(key: str, amount: float, dest: str): 
    if key not in keypairs:
        raise HTTPException(status_code=404, detail="Key not found")
    return comx.unstake(keypairs[key], amount, dest)



# Run the FastAPI app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)