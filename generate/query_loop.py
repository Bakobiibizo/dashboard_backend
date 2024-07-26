import time
import json
import asyncio
from loguru import logger

from data_models import comx


QUERY_MAP = {
    "query_map": comx.query_map,
    "curator_applications": comx.query_map_curator_applications,
    "proposals": comx.query_map_proposals,
    "weights": comx.query_map_weights,
    "key": comx.query_map_key,
    "address": comx.query_map_address,
    "emission": comx.query_map_emission,
    "pending_emission": comx.query_map_pending_emission,
    "subnet_emission": comx.query_map_subnet_emission,
    "subnet_consensus": comx.query_map_subnet_consensus,
    "incentive": comx.query_map_incentive,
    "dividend": comx.query_map_dividend,
    "regblock": comx.query_map_regblock,
    "lastupdate": comx.query_map_lastupdate,
    "stakefrom": comx.query_map_stakefrom,
    "staketo": comx.query_map_staketo,
    "delegationfee": comx.query_map_delegationfee,
    "tempo": comx.query_map_tempo,
    "min_allowed_weights": comx.query_map_min_allowed_weights,
    "max_allowed_weights": comx.query_map_max_allowed_weights,
    "max_allowed_uids": comx.query_map_max_allowed_uids,
    "founder": comx.query_map_founder,
    "founder_share": comx.query_map_founder_share,
    "incentive_ratio": comx.query_map_incentive_ratio,
    "trust_ratio": comx.query_map_trust_ratio,
    "legit_whitelist": comx.query_map_legit_whitelist,
    "subnet_names": comx.query_map_subnet_names,
    "balances": comx.query_map_balances,
    "registration_blocks": comx.query_map_registration_blocks,
    "name": comx.query_map_name,
    "subnet_burn": comx.query_map_subnet_burn,
}

QUERY_MAP_CHOICES = list(QUERY_MAP.keys())


def walk_dict(data_dict=None):
    data_dict = data_dict or comx.__class__.__dict__
    final_dict = {}
    for key, value in data_dict.items():
        logger.debug(key, value.__repr__())
        if key.startswith("query_map"):
            value = key
            key = key.replace("query_map_", "")
            final_dict[key] = value
            QUERY_MAP_CHOICES.append(key)
    QUERY_MAP = final_dict

    with open("main_reports/functions.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(QUERY_MAP, indent=4))
    return QUERY_MAP


def get_query_map(query_map_choice):
    logger.info(f"Getting query map: {query_map_choice}")
    query_map = QUERY_MAP[query_map_choice]()

    logger.debug(f"query_map: {query_map}")
    with open(
        f"query_maps/query_map_{query_map_choice}.json", "w", encoding="utf-8"
    ) as f:
        f.write(json.dumps(query_map, indent=4))


async def get_query_maps():
    while True:
        for key in QUERY_MAP_CHOICES:
            if key == "query_map":
                continue
            get_query_map(key)
        time.sleep(1800)


REPORT_MAP = {
    "eden": "main_reports/eden.json",
    "personal": "main_reports/personal.json",
    "staff": "main_reports/staff.json",
    "huck": "main_reports/huck.json",
}


if __name__ == "__main__":
    asyncio.run(get_query_maps())