import json
from substrateinterface import Keypair
from wallet.get_key_dict import get_key_dict
from pathlib import Path


def get_keypair(key_path, keydir="~/.commune/key"):
    keyring = {}
    ignore_list = ("nix", "unk", "mul")
    key_dict = get_key_dict(key_path)
    for key, value in key_dict.items():
        name = value["name"]
        if name[:3] in ignore_list:
            continue
        keypath = Path(f"{keydir}/{name}.json").expanduser()
        with open(keypath, "r", encoding="utf-8") as f:
            json_data = json.loads(f.read())["data"]
            data = json.loads(json_data)
            keyring[key] = Keypair(
                data["ss58_address"],
                data["public_key"],
                data["private_key"]
            )
    return keyring


if __name__ == "__main__":
    keypair = get_keypair("main_reports/eden.json")
    print(keypair)
