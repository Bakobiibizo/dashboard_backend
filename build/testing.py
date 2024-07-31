import json
from pathlib import Path
from wallet.commands.comx_command_manager import ComxCommandManager, CONFIG


manager = ComxCommandManager()



def vote(key, subnet):
    query_maps = manager.get_subnet_maps(subnet)["weights"]
    with open("test.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(query_maps, indent=4))
    
vote("key", 10)