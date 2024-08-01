import os
import json
import asyncio
from pathlib import Path
from wallet.data_models import Settings
from wallet.encryption.wallet import Wallet

CONFIG = Settings()

logger = CONFIG.loguru_logger
logger.bind(name="comx_command_manager")

comx = CONFIG.communex_client 
wallet = Wallet()


class ComxCommandManager:
    def __init__(self):
        logger.info("Initializing ComxCommandManager...")
        self.querymap_path = CONFIG.querymap_path
        self.query_maps = {}
        self.commands_list = []
        self.command_whitelist = ["register", "transfer"]
        self.commands_string = ""
        self.commands = {}
        self.data_maps = {}
        self.keypair = None
        self.subnet_query_list = CONFIG.subnet_query_list 
        self.subnet_list = CONFIG.subnets
        self.rootnet = 0
        self.init_manager()
        
    def init_manager(self):
        self.get_command_list()
        self.get_commands_string()
        self.get_commands_dict()
        self.get_query_map_list()
        
    def get_keypair(self):
        logger.info("Getting keypair...")
        return self.keypair
    
    def check_path(self, path):
        if isinstance(path, str):
            path = Path(path)
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            
    def get_command_list(self):
        logger.info("Getting command list...")
        commands = comx.__dir__()
        self.commands_list = [command for command in commands if not command.startswith("_")]
        return self.commands_list

    def get_commands_string(self):
        logger.info("Getting commands string...")
        self.commands_string = "\n".join(self.commands_list)
        return self.commands_string
        
    def get_commands_dict(self):
        logger.info("Getting commands dict...")
        for command in self.commands_list:
            self.commands[command] = comx.__getattribute__(command)
        return self.commands
    
    def _execute_command(self, command_name, **kwargs):
        logger.info(f"Executing command: {command_name}")        
        if command_name in self.command_whitelist:
            return self.commands[command_name](**kwargs)
        else:
            raise ValueError(f"Command {command_name} not found. Available commands: {self.commands_list}")
        
    def get_query_map_list(self):
        logger.info("Getting query map list...")
        for command in self.commands_list:
            if command.startswith("query_map_"):
                self.query_maps[command.split("query_map_")[1].split(".")[0]] = comx.__getattribute__(command)
        return self.query_maps
        
    def execute_query_map(self, query_map_name, **kwargs):
        logger.info(f"Executing query map: {query_map_name}")
        if query_map_name not in self.query_maps:
            raise ValueError(f"Query map {query_map_name} not found")
        return self.query_maps[query_map_name](**kwargs)
        
    def get_all_query_map(self):
        logger.info("Getting all query maps...")
        query_maps = {}
        if self.querymap_path.exists():
            for query_map in self.querymap_path.glob("*.json"):
                query_maps[query_map] = json.loads(query_map.read_text(encoding="utf-8"))
        else:
            self.querymap_path.mkdir(parents=True, exist_ok=True)
            self.execute_all_query_map()
        return query_maps

    def get_subnet_maps(self, subnet):
        logger.info("Getting subnet maps...")
        query_maps = {}
        self.check_path(self.querymap_path)
        for query_map in self.querymap_path.glob("*.json"):
            name = query_map.name.split(".")[0].replace("query_map_", "")
            if name in self.subnet_query_list:
                query_maps[name] = json.loads(query_map.read_text(encoding="utf-8"))[f"{subnet}"]
            else:
                query_maps[name] = json.loads(query_map.read_text(encoding="utf-8"))
        return query_maps
    
    def load_subnet_query_data(self, query_name, subnet):
        with open(f"{CONFIG.querymap_path}/{subnet}/query_map_{query_name}.json", "r", encoding="utf-8") as f:
            return json.loads(f.read())
        
    def execute_all_query_map(self):
        logger.info("Gathering all query maps...")
        ignore_list = ["min_stake", "max_stake", "vote_mode_subnet"]
        query_maps = []
        for query_map_name in self.query_maps:
            if query_map_name in ignore_list:
                continue
            if query_map_name in self.subnet_query_list:
                for subnet in self.subnet_list:
                    subnet_path = Path(f"{self.querymap_path}/{subnet}")
                    self.check_path(subnet_path)
                    querymap = self.execute_query_map(query_map_name=query_map_name, netuid=subnet, extract_value=False)
                    save_path = Path(f"{self.querymap_path}/{subnet}/{query_map_name}.json")
                    save_path.write_text(json.dumps(querymap, indent=4), encoding="utf-8")
                    query_maps.append(querymap)
            if query_map_name == "immunity_period":
                querymap = self.execute_query_map(query_map_name=query_map_name, extract_value=False)
            else:
                querymap = self.execute_query_map(query_map_name=query_map_name)    
            save_path = Path(f"{self.querymap_path}/{query_map_name}.json")
            self.check_path(self.querymap_path)
            save_path.write_text(json.dumps(querymap, indent=4), encoding="utf-8")
            query_maps.append(querymap)
            
    async def query_map_loop_event(self):
        """Query map loop event """
        
        while True:
            await asyncio.sleep(180)
            self.execute_all_query_map()

async def run_query_map_loop():
    manager = ComxCommandManager()
    return await manager.query_map_loop_event()
        
if __name__ == "__main__":
    manager = asyncio.run(run_query_map_loop())
    
