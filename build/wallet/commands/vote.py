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
    
    


def get_vali_uid(subnet):
    return SUBNET_VALIDATORS[str(subnet)]["uid"]
    
def get_miner_uids(subnet):
    return [value["uid"] for value in construct_miners_dict(subnet).values()]
    
def construct_weights(subnet, vali_uid):
    miner_uids = get_miner_uids(subnet)
    uids = []
    weights = []
    vali_weights = get_subnet_query_data("weights", subnet)[str(vali_uid)]
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


    
    