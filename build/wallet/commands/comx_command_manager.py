import os
import json
import asyncio
from pathlib import Path
from wallet.data_models import Settings

CONFIG = Settings()

logger = CONFIG.loguru_logger
logger.bind(name="comx_command_manager")

comx = CONFIG.communex_client 


class ComxCommandManager:
    def __init__(self):
        logger.info("Initializing ComxCommandManager...")
        self.querymap_path = CONFIG.querymap_path
        self.query_maps = {}
        self.commands_list = []
        self.commands_string = ""
        self.commands = {}
        self.data_maps = {}
        self.keypair = None
        self.query_subnet_list = ["weights", "keys", "addresses"]
        self.subnet_list = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 17]
        self.rootnet = 0
        self.init_manager()
        
    def init_manager(self):
        self.get_command_list()
        self.get_commands_string()
        self.get_commands_dict()
        self.get_query_map_list()
        
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

    def get_query_map_list(self):
        logger.info("Getting query map list...")
        for command in self.commands_list:
            if command.startswith("query_map_"):
                self.query_maps[command] = comx.__getattribute__(command)
        return self.query_maps
                
    def _execute_command(self, command_name, **kwargs):
        logger.info(f"Executing command: {command_name}")
        if command_name not in self.commands:
            raise ValueError(f"Command {command_name} not found. Available commands: {self.commands_list}")
        else:
            return self.commands[command_name](**kwargs)
        
    def execute_query_map(self, query_map_name, **kwargs):
        logger.info(f"Executing query map: {query_map_name}")
        if query_map_name not in self.query_maps:
            raise ValueError(f"Query map {query_map_name} not found")
        return self.data_maps[query_map_name](**kwargs)
        
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

    def get_keypair(self):
        logger.info("Getting keypair...")
        return self.keypair
    
    def execute_all_query_map(self):
        logger.info("Gathering all query maps...")
        ignore_list = ["query_map_min_stake", "query_map_max_stake", "query_map_vote_mode_subnet"]
        query_maps = []
        for query_map_name in self.query_maps:
            if query_map_name in ignore_list:
                continue
            if query_map_name in self.query_subnet_list:
                for subnet in self.subnet_list:
                    subnet_path = Path(f"{self.querymap_path}/{subnet}")
                    subnet_path.mkdir(parents=True, exist_ok=True)
                    querymap = self.execute_query_map(query_map_name=query_map_name, netuid=subnet, extract_value=False)
                    save_path = Path(f"{self.querymap_path}/{subnet}/{query_map_name}.json")
                    save_path.write_text(json.dumps(querymap, indent=4), encoding="utf-8")
                    query_maps.append(querymap)
            if query_map_name == "query_map_immunity_period":
                querymap = self.execute_query_map(query_map_name=query_map_name, extract_value=False)
            else:
                querymap = self.execute_query_map(query_map_name=query_map_name)    
            save_path = Path(f"{self.querymap_path}/{query_map_name}.json")
            save_path.write_text(json.dumps(querymap, indent=4), encoding="utf-8")
            query_maps.append(querymap)
            
    def load_data_maps(self, query_maps_path):
        query_maps = {}
        query_path = query_maps_path or CONFIG.querymap_path
        if not query_path.exists():
            query_path.mkdir(parents=True, exist_ok=True)
            return query_maps
        for root, dirs, files in os.walk(query_path):
            for dir in dirs:
                if 
            for file in files:
                name = file.split(".")[0]
                if file.endswith(".json"):
                    query_maps[name] = json.loads(Path(os.path.join(root, file)).read_text(encoding="utf-8"))
        self.data_maps = query_maps
        return self.data_maps

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
    print(manager.commands_list)
    
