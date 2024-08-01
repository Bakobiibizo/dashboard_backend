import subprocess
import json
import os
from wallet.encryption.wallet import Wallet
from wallet.commands.comx_command_manager import ComxCommandManager, CONFIG
from wallet.commands.transfer import transfer

manager = ComxCommandManager()
wallet = Wallet()


def get_funding_key(key="vali::eden00"):
    
    keydict = wallet.get_encrypted_key_dict(CONFIG.key_dict_path)
    unecrypted = wallet.decrypt_and_decode(keydict)
    keyring = wallet.load_keyring(unecrypted)
    return keyring[f"{key}.json"]

FUNDING_KEY = get_funding_key()

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
    command = ["comx", "module", "register", f"{name}", f"{keyname}", "--ip", f"{ip}", "--port", f"{port}", "--netuid", f"{subnet}"]
    print(command)
    # try:
        # subprocess.run(command, check=True)
    # except subprocess.CalledProcessError as e:
        # print(e)

        
def bulk_register():
    for subnet in CONFIG.subnets:
        for key, data in MINER_KEYS.items():
            register(data["name"], data["key"], "127.0.0.1", "8000", subnet)
            
def fund_key(key):
    transfer(FUNDING_KEY, "10", key)