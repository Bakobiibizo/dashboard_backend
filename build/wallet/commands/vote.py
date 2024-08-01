import os
import json
from wallet.commands.comx_command_manager import ComxCommandManager
from wallet.encryption.wallet import Wallet
from wallet.data_models import Settings

CONFIG = Settings()

manager = ComxCommandManager()
wallet = Wallet()

keyring = wallet.keyring

print(keyring)

#QUERY_MAPS = manager.execute_all_query_map()

SUBNET_VALIDATORS = CONFIG.subnet_validators
SUBNET_LIST = CONFIG.subnets
    
    
def construct_miners_dict(subnet):    
    miner_key_path = CONFIG.miner_key_path
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

def get_vali_uid(subnet):
    return SUBNET_VALIDATORS[str(subnet)]["uid"]
    
def get_miner_uids(subnet):
    return [value["uid"] for value in construct_miners_dict(subnet).values()]
    
def construct_weights(subnet, vali_uid):
    miner_uids = get_miner_uids(subnet)
    uids = []
    weights = []
    vali_weights = manager.load_subnet_query_data("weights", subnet)[str(vali_uid)]
    for uid, weight in vali_weights:
        uids.append(uid)
        weights.append(weight)
    max_value = max(weights)
    for uid in miner_uids:
        if uid in uids:
            if uid == vali_uid:
                continue
            index = uids.index(uid)
            weights[index] = max_value - weights[index]
        else:
            weights.append(max_value)
    return uids, weights
    
    
def vote():
    for subnet in CONFIG.subnets:
        if subnet in [1, 2]:
            continue
        subnet = 10
        uids, weights = construct_weights(subnet, CONFIG.subnet_validators[f"{subnet}"]["uid"])
    print(weights)
    print(uids)
    
    
vote()


    
    