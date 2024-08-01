import subprocess
import json
import os
from wallet.commands.comx_command_manager import ComxCommandManager, CONFIG


manager = ComxCommandManager()

def construct_miners_dict(subnet):    
    miner_key_path = "wallet/tigerking"
    miners_dict = {}
    for key in os.listdir(f"{miner_key_path}"):
        with open(f"{miner_key_path}/{key}", "r", encoding="utf-8") as f:
            miner_key = json.loads(f.read())["data"]
            miner_data = json.loads(miner_key)
            name = key.split(".")[0]
            key = miner_data["ss58_address"]
            uid_map = manager.load_subnet_query_data("key", subnet)
            for uid, uidkey in uid_map.items():
                if key == uidkey:
                    miners_dict[name] = {
                        "uid": uid,
                        "name": name,
                        "key": key
                    }
                
    return miners_dict
    
for subnet in CONFIG.subnets:

def register(name, keyname, ip, port, subnet):
    command = ["comx", "module", "register", f"{name}", f"{keyname}", "--ip" f"{ip}", "--port" f"{port}", "--netuid" f"{subnet}"]
    print(command)