from pathlib import Path
from communex._common import get_node_url
from communex.client import CommuneClient
from datetime import datetime
from enum import Enum
import json

comx = CommuneClient(get_node_url())


class QUERY_MAP_CHOICES(Enum):
    weights: str = "weights"
    key: str = "key"
    address: str = "address"
    emission: str = "emission"
    incentive: str = "incentive"
    dividend: str = "dividend"
    regblock: str = "regblock"
    lastupdate: str = "lastupdate"
    total_stake: str = "total_stake"
    stakefrom: str = "stakefrom"
    delegationfee: str = "delegationfee"
    tempo: str = "tempo"
    min_allowed_weights: str = "min_allowed_weights"
    max_allowed_weights: str = "max_allowed_weights"
    max_allowed_uids: str = "max_allowed_uids"
    founder: str = "founder"
    founder_share: str = "founder_share"
    incentive_ratio: str = "incentive_ratio"
    trust_ratio: str = "trust_ratio"
    subnet_names: str = "subnet_names"
    balances: str = "balances"
    registration_blocks: str = "registration_blocks"


QUERY_MAP = {
    "weights": comx.query_map_weights,
    "key": comx.query_map_key,
    "address": comx.query_map_address,
    "emission": comx.query_map_emission,
    "incentive": comx.query_map_incentive,
    "dividend": comx.query_map_dividend,
    "regblock": comx.query_map_regblock,
    "lastupdate": comx.query_map_lastupdate,
    "total_stake": comx.query_map_staketo,
    "stakefrom": comx.query_map_stakefrom,
    "delegationfee": comx.query_map_delegationfee,
    "tempo": comx.query_map_tempo,
    "min_allowed_weights": comx.query_map_min_allowed_weights,
    "max_allowed_weights": comx.query_map_max_allowed_weights,
    "max_allowed_uids": comx.query_map_max_allowed_uids,
    "founder": comx.query_map_founder,
    "founder_share": comx.query_map_founder_share,
    "incentive_ratio": comx.query_map_incentive_ratio,
    "trust_ratio": comx.query_map_trust_ratio,
    "subnet_names": comx.query_map_subnet_names,
    "balances": comx.query_map_balances,
    "registration_blocks": comx.query_map_registration_blocks,
}


def recordtime():
    time = datetime.now().timestamp()
    with open("query_maps/time.json", "w", encoding="utf-8") as f:
        save_time = {"time": time}
        print(time)
        f.write(json.dumps(save_time))


def update_query_maps():
    for choice_key in QUERY_MAP_CHOICES.__iter__():
        print(f"Updating {choice_key}")
        query_map = QUERY_MAP[choice_key.value]()
        with open(f"query_maps/{choice_key.value}.json", "w", encoding="utf-8") as f:
            f.write(json.dumps(query_map))
    recordtime()
    print("Updated")


def check_time():
    time = datetime.now().timestamp()
    time_path = Path("query_maps/time.json")
    if not time_path.exists():
        time_path.write_text('{"time": 0}', encoding="utf-8")
    with open("query_maps/time.json", "r", encoding="utf-8") as f:
        oldtime = json.load(f)["time"]
        print(time)
        timediff = time - oldtime
        if timediff > 600:
            print("Stale query maps, updating")
            update_query_maps()
    print("Query maps up to date")


def get_query_map(keypath_name: str | QUERY_MAP_CHOICES):
    check_time()
    map_key = str(keypath_name)
    if map_key.startswith("QUERY_MAP"):
        query_key = map_key.replace("QUERY_MAP_CHOICES.", "")
    with open(f"query_maps/{query_key}.json", "r", encoding="utf-8") as f:
        return json.load(f)


if __name__ == "__main__":
    print(update_query_maps())
