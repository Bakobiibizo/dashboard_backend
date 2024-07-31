import json
from pathlib import Path
from wallet.commands.comx_command_manager import ComxCommandManager, CONFIG


manager = ComxCommandManager()

query_maps = manager.get_subnet_maps(10)

