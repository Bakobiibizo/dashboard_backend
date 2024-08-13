import os
import json
import asyncio
from pathlib import Path
from typing import Dict, Any, List
from wallet.data_models import Settings
from wallet.encryption.wallet import Wallet
from communex.client import CommuneClient
from communex._common import get_node_url

CONFIG = Settings()
logger = CONFIG.loguru_logger.bind(name="comx_command_manager")

class ComxCommandManager:
    def __init__(self):
        logger.info("Initializing ComxCommandManager...")
        self.querymap_path = CONFIG.querymap_path
        self.query_maps: Dict[str, Any] = {}
        self.commands_list: List[str] = []
        self.command_whitelist = ["register_module", "transfer"]
        self.commands: Dict[str, Any] = {}
        self.subnet_query_list = CONFIG.subnet_query_list 
        self.subnet_list = CONFIG.subnets
        self.rootnet = 0
        node_url = get_node_url()
        try:
            self.comx = CommuneClient(node_url)
        except Exception as e:
            logger.error(f"Error initializing ComxCommandManager: {str(e)}\n{node_url}")
        self.wallet = Wallet()
        self.key_data = {}

    async def init_manager(self):
        await self.get_command_list()
        await self.get_commands_dict()
        await self.get_query_map_list()
        
    def check_path(self, path: Path):
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            
    async def get_command_list(self):
        logger.info("Getting command list...")
        self.commands_list = [command for command in dir(self.comx) if not command.startswith("_")]
        return self.commands_list

    async def get_commands_dict(self):
        logger.info("Getting commands dict...")
        for command in self.commands_list:
            self.commands[command] = getattr(self.comx, command)
        return self.commands
    
    async def execute_command(self, command_name: str, **kwargs):
        logger.info(f"Executing command: {command_name}")        
        if command_name in self.command_whitelist:
            command = self.commands.get(command_name)
            if command is None:
                raise ValueError(f"Command {command_name} not found")
            if asyncio.iscoroutinefunction(command):
                return await command(**kwargs)
            else:
                return command(**kwargs)
        else:
            raise ValueError(f"Command {command_name} not in whitelist. Available commands: {self.commands_list}")
        
    async def get_query_map_list(self):
        logger.info("Getting query map list...")
        for command in self.commands_list:
            if command.startswith("query_map_"):
                query_name = command.split("query_map_")[1]
                self.query_maps[query_name] = getattr(self.comx, command)
        return self.query_maps
        
    async def execute_query_map(self, query_map_name: str, **kwargs):
        logger.info(f"Executing query map: {query_map_name}")
        if query_map_name not in self.query_maps:
            raise ValueError(f"Query map {query_map_name} not found")
        query_map = self.query_maps[query_map_name]
        if asyncio.iscoroutinefunction(query_map):
            return await query_map(**kwargs)
        else:
            return query_map(**kwargs)
        
    async def get_all_query_map(self):
        logger.info("Getting all query maps...")
        query_maps = {}
        self.check_path(self.querymap_path)
        for query_map in self.querymap_path.glob("*.json"):
            query_maps[query_map.stem] = json.loads(query_map.read_text(encoding="utf-8"))
        if not query_maps:
            await self.execute_all_query_map()
            query_maps = await self.get_all_query_map()
        return query_maps

    async def get_subnet_maps(self, subnet: int):
        logger.info(f"Getting subnet maps for subnet {subnet}...")
        query_maps = {}
        self.check_path(self.querymap_path)
        for query_map in self.querymap_path.glob("*.json"):
            name = query_map.stem.replace("query_map_", "")
            data = json.loads(query_map.read_text(encoding="utf-8"))
            if name in self.subnet_query_list:
                query_maps[name] = data.get(str(subnet), {})
            else:
                query_maps[name] = data
        return query_maps
    
    async def load_subnet_query_data(self, query_name: str, subnet: int):
        file_path = self.querymap_path / f"{subnet}" / f"query_map_{query_name}.json"
        if not file_path.exists():
            logger.warning(f"Query map file not found: {file_path}")
            return {}
        return json.loads(file_path.read_text(encoding="utf-8"))
        
    async def execute_all_query_map(self):
        logger.info("Gathering all query maps...")
        ignore_list = ["min_stake", "max_stake", "vote_mode_subnet", "delegationfee", "immunity_period"]
        for query_map_name in self.query_maps:
            if query_map_name in ignore_list:
                continue
            try:
                if query_map_name in self.subnet_query_list:
                    for subnet in self.subnet_list:
                        subnet_path = self.querymap_path / str(subnet)
                        self.check_path(subnet_path)
                        querymap = await self.execute_query_map(query_map_name=query_map_name, netuid=subnet, extract_value=False)
                        save_path = subnet_path / f"{query_map_name}.json"
                        save_path.write_text(json.dumps(querymap, indent=4), encoding="utf-8")
                else:
                    querymap = await self.execute_query_map(query_map_name=query_map_name)    
                    save_path = self.querymap_path / f"{query_map_name}.json"
                    save_path.write_text(json.dumps(querymap, indent=4), encoding="utf-8")
            except Exception as e:
                logger.error(f"Error executing query map {query_map_name}: {str(e)}")

    async def query_map_loop(self):
        while True:
            try:
                await self.execute_all_query_map()
                await asyncio.sleep(180)
            except Exception as e:
                logger.error(f"Error in query map loop: {str(e)}")
                await asyncio.sleep(60)  # Wait a bit before retrying


    async def open_query_map(self, query_map_name: str):
        with open(f"static/query_maps/{query_map_name}.json", "r") as f:
            return await json.loads(f.read())

    async def get_key_data(self):
        key_data_names = ["balances", "staketo", "stakefrom", "dividends", "emissions", "incentive", "weights", "key", "address"]
        for key_name in key_data_names:
            datapoint = await self.open_query_map(key_name)
            
            self.key_data[key_name] = {
                ""
            }
            

async def run_query_map_loop():
    manager = ComxCommandManager()
    await manager.init_manager()
    task = asyncio.create_task(await manager.query_map_loop())
    asyncio.run(task)

if __name__ == "__main__":
    asyncio.run(run_query_map_loop())