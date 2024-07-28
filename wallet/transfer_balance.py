import argparse
import json
from communex.client import CommuneClient
from communex._common import get_node_url

comx = CommuneClient(get_node_url())

def transfer_balance(key, amount, destination):
    command = ["comx", "transfer-balance", "--key", key, "--amount", amount, "--destination" destination]

def parseargs():
    parser = argparse.ArgumentParser()
    parser.add_argument("--key", type=str, required=True)
    parser.add_argument("--amount", type=str, required=True)
    parser.add_argument("--destination", type=str, required=True)
    return parser.parse_args()

if __name__ == "__main__":
    args = parseargs()
    print(comx.transfer_balance(args.key, args.amount, args.destination))