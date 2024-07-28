from communex.client import CommuneClient
from communex._common import get_node_url
from communex.compat.key import Keypair, Ss58Address
from pathlib import Path
import time
import json
import os
import io

comx = CommuneClient(get_node_url())


def get_balance_map():
    with open("query_maps/balances.json", "r", encoding="utf-8") as f:
        return json.load(f)


def get_balance(ss58key):
    query_map = get_balance_map()

    return query_map[ss58key]["data"]["free"]


def get_staketo_map():
    with open("querymaps/staketo.json", "r", encoding="utf-8") as f:
        return json.load(f)


def get_staketo(ss58key):
    query_map = get_staketo_map()
    staketo = 0
    staketo_list = query_map[ss58key]
    if len(staketo_list) > 0:
        for stake in staketo_list:
            staketo += stake[1]
    return staketo


def get_stakefrom_map():
    with open("querymaps/stakefrom.json", "r", encoding="utf-8") as f:
        return json.load(f)


def get_stakefrom(ss58key):
    query_map = get_stakefrom_map()
    stakefrom = 0
    stakefrom_list = query_map[ss58key]
    if len(stakefrom_list) > 0:
        for stake in stakefrom_list:
            stakefrom += stake[1]
    return stakefrom


def get_all_balances(key_dict):
    min_bal = 0.5
    dictionary = {}
    try:
        for ss58key, value in key_dict.items():
            name = value["name"]
            balance = get_balance(ss58key)
            print(balance)
            stake = get_staketo(ss58key)
            print(stake)
            total_balance = balance + stake
            stake_from = get_stakefrom(ss58key)
            print(stake_from)
            if total_balance > min_bal:
                dictionary[name] = {
                    "address": ss58key,
                    "mnemonic": value["mnemonic"],
                    "balance": balance,
                    "stake": stake,
                    "total": total_balance,
                    "stake_from": stake_from,
                }
        with open("output.json", "w", encoding="utf-8") as f:
            json.dump(dictionary, f, indent=4)
    except Exception as e:
        print(e)


def get_balances(key_path):
    with open(key_path, "r", encoding="utf-8") as f:
        key_data = json.load(f)
    key_dict = {}
    lines = []
    balance_querymap = get_balance_map()
    staketo_querymap = get_staketo_map()
    stakefrom_querymap = get_stakefrom_map()
    try:
        for ss58key, value in key_data.items():
            balance = 0
            staketo = 0
            stakefrom = 0
            total = 0

            if ss58key in balance_querymap.keys():
                balance = round((get_balance(ss58key) / 1_000_000_000), 2) or 0
            if ss58key in staketo_querymap.keys():
                staketo = round((get_staketo(ss58key) / 1_000_000_000), 2) or 0
            if ss58key in stakefrom_querymap.keys():
                stakefrom = round((get_stakefrom(ss58key) / 1_000_000_000), 2) or 0
            total = round((balance + staketo), 2) or 0
            if total > 5000 or stakefrom > 5000:
                print(balance)
                print(staketo)
                print(stakefrom)
                key_dict[ss58key] = {}
                key_dict[ss58key]["balance"] = balance
                key_dict[ss58key]["stake"] = staketo
                key_dict[ss58key]["total"] = total
                key_dict[ss58key]["stake_from"] = stakefrom
                lines.append(f"{ss58key}: {total}")
                lines.append(f"Name: {value['name']}")
                lines.append(f"Balance: ${key_dict[ss58key]['balance']}")
                lines.append(f"Staketo: ${key_dict[ss58key]['stake']}")
                lines.append("--------")
                lines.append(f"Total: ${key_dict[ss58key]['total']}")
                lines.append(f"StakeFrom: ${key_dict[ss58key]['stake_from']}")
                lines.append("")

        with open("output.json", "w", encoding="utf-8") as f:
            f.write(json.dumps(key_dict, indent=4))
        with open("output.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
    except Exception as e:
        print(e)


def check_keyring(key_path):
    key_dict = {}
    with open(key_path, "r", encoding=("utf-8")) as f:
        data = f.read() if isinstance(f, io.TextIOWrapper) else json.loads(f.read())
        print(data)
        for keyname, keydata in data.items():
            keydata = json.loads(keydata)

            if "ss58_address" not in keydata:
                continue
            key = keydata["ss58_address"]
            if "mnemonic" not in keydata:
                continue
            mnemnoic = keydata["mnemonic"]
            if "path" not in keydata:
                continue
            key_dict[key] = {"key": key, "mnemonic": mnemnoic, "name": keyname}
    with open("key_dict.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(key_dict, indent=4))


def get_local_keys(key_path):
    key_ring = {}
    keypath = Path(key_path)
    keys = keypath.glob("*.json")
    for key in keys:
        if "key2address" in key.name:
            continue
        with open(key, "r", encoding="utf-8") as f:
            data = json.loads(f.read())["data"]
            data = json.loads(data)
            keyring = {
                "key": data["ss58_address"],
                "mnemonic": data["mnemonic"],
                "name": data["path"],
                "crypto_type": data["crypto_type"],
                "derive_path": data["derive_path"],
                "public_key": data["public_key"],
                "private_key": data["private_key"],
                "ss58_format": data["ss58_format"],
            }
            key_ring[keyring["key"]] = keyring
    with open("key_dict.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(key_ring, indent=4))
    get_balances("key_dict.json")


if __name__ == "__main__":
    get_balances("wallet/key_store/eden_keys.json")
