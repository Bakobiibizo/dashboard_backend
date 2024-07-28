import json
from communex.client import CommuneClient
from communex._common import get_node_url
from data_models import URL


comx = CommuneClient(get_node_url())


def get_key_dict(key_path):
    key_dict = {}
    with open(key_path, "r", encoding=("utf-8")) as f:
        data = json.loads(f.read())
        for key, keydata in data.items():

            if "key" not in keydata:
                continue
            if "name" not in keydata:
                continue
            key = keydata["key"]
            key_dict[key] = {"key": key, "name": keydata["name"]}
    return key_dict


if __name__ == "__main__":
    key_dict = get_key_dict("main_reports/eden.json")
    print(key_dict)
