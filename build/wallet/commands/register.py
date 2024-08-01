import subprocess
import json
import os
from wallet.encryption.wallet import Wallet
from wallet.commands.comx_command_manager import ComxCommandManager, CONFIG
from wallet.commands.transfer import transfer
from communex.client import CommuneClient

manager = ComxCommandManager()
wallet = Wallet()


def get_miner_keys():
    miner_keys = {}
    keypaths = CONFIG.miner_key_path.iterdir()
    for keypath in keypaths:
        json_key = json.loads(keypath.read_text("utf-8"))["data"]
        key = json.loads(json_key)
        miner_data = {"name": key["path"], "key": key["ss58_address"]}
        miner_keys[miner_data["name"]] = miner_data
    return miner_keys


MINER_KEYS = get_miner_keys()


def register(name, keyname, ip, port, subnet):
    address = f"{ip}:{port}"
    try:
        result = manager.get_commands_dict()["register_module"](key=name, name=keyname, address=address, subnet=subnet)
        if result.is_success:
            print(result.is_success)
            return result.extrinsic
        else:
            print(result.error)
    except Exception as e:
        print(e)
        return
        
def bulk_register(miner_keys):
    for subnet in CONFIG.subnets:
        for i, key in enumerate(miner_keys.keys()):
            register(key, key, "127.0.0.1", 8000 + i, subnet)
            
def fund_keys(funding_key, key_names, amount):
    for key in key_names:
        transfer(funding_key, amount, key)
        
