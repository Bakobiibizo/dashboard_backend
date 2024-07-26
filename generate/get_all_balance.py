import json
from wallet.get_keyring import get_keyring


def get_balance_map():
    with open("query_maps/balances.json", "r", encoding="utf-8") as f:
        return json.load(f)


def get_staketo_map():
    with open("query_maps/staketo.json", "r", encoding="utf-8") as f:
        return json.load(f)


def get_stakefrom_map():
    with open("query_maps/stakefrom.json", "r", encoding="utf-8") as f:
        return json.load(f)


def get_balance(ss58key):
    query_map = get_balance_map()

    return query_map[ss58key]["data"]["free"]


def get_staketo(ss58key):
    query_map = get_staketo_map()
    staketo = 0
    staketo_list = query_map[ss58key]
    if len(staketo_list) > 0:
        for stake in staketo_list:
            staketo += stake[1]
    return staketo


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
            balance = get_balance(ss58key)
            print(balance)
            stake = get_staketo(ss58key)
            print(stake)
            total_balance = balance + stake
            stake_from = get_stakefrom(ss58key)
            print(stake_from)
            if total_balance > min_bal:
                name = value["name"]
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
    return dictionary


def get_balances(key_data):
    key_dict = {}
    lines = []
    balance_querymap = get_balance_map()
    staketo_querymap = get_staketo_map()
    stakefrom_querymap = get_stakefrom_map()
    try:
        for ss58key, value in key_data.items():
            name = value["name"]
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

            print("")
            print(f"Balance    {balance}")
            print(f"StakeTo    {staketo}")
            print("            -----------")
            print(f"Total      {total}")
            print(f"StakeFrom  {stakefrom}")
            print("            ===========")

            key_dict[ss58key] = {
                "key": ss58key,
                "name": name,
                "balance": balance,
                "stake": staketo,
                "total": total,
                "stake_from": stakefrom,
            }
            lines.extend(
                (
                    "",
                    f"Balance    {balance}",
                    f"StakeTo    {staketo}",
                    "            -----------",
                    f"Total      {total}",
                    f"StakeFrom  {stakefrom}",
                    "            ===========",
                )
            )
    except Exception as e:
        print(e)
    return key_dict


def check_keyring(key_path):
    key_dict = get_keyring(key_path)
    key_dict = get_balances(key_dict)
    with open("main_reports/keyring.json", "w", encoding="utf-8") as f:
        json.dump(key_dict, f, indent=4)
    return key_dict


if __name__ == "__main__":
    check_keyring("eden")
