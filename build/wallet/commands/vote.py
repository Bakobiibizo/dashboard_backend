import os
import json
import asyncio
from typing import Dict, List, Tuple
from wallet.commands.comx_command_manager import ComxCommandManager
from wallet.encryption.wallet import Wallet
from wallet.data_models import Settings

CONFIG = Settings()
logger = CONFIG.loguru_logger.bind(name="vote")

class VotingService:
    def __init__(self):
        self.manager = ComxCommandManager()
        self.wallet = Wallet()
        self.wallet.init_keyring(CONFIG.key_dict_path)
        self.keyring = self.wallet.keyring

    async def construct_miners_dict(self, subnet: int) -> Dict[str, Dict]:
        logger.info(f"Constructing miners dict for subnet {subnet}...")
        miners_dict = {}
        miner_key_path = CONFIG.miner_key_path
        uid_map = await self.manager.load_subnet_query_data("key", subnet)

        for key in os.listdir(miner_key_path):
            with open(os.path.join(miner_key_path, key), "r", encoding="utf-8") as f:
                miner_key = json.loads(f.read())["data"]
                miner_data = json.loads(miner_key)
                name = key.split(".")[0]
                key = miner_data["ss58_address"]
                for uid, uidkey in uid_map.items():
                    if key == uidkey:
                        miners_dict[name] = {
                            "uid": uid,
                            "name": name,
                            "key": key
                        }
        logger.debug(f"Miners dict for subnet {subnet}: {miners_dict}")
        return miners_dict

    async def get_vali_uid(self, subnet: int) -> int:
        logger.info(f"Getting vali uid for subnet {subnet}...")
        return CONFIG.subnet_validators[f"{subnet}"]["uid"]

    async def construct_weights(self, subnet: int, vali_uid: int) -> Tuple[List[int], List[int]]:
        logger.info(f"Constructing weights for subnet {subnet}...")
        uids = []
        weights = []
        vali_weights = await self.manager.load_subnet_query_data("weights", subnet)
        vali_weights = vali_weights[str(vali_uid)]

        for uid, weight in vali_weights:
            uids.append(uid)
            weights.append(weight)

        max_value = max(weights)
        encrypted = self.wallet.get_encrypted_key_dict(CONFIG.key_dict_path)
        key_dict = self.wallet.decrypt_and_decode(encrypted)

        for key in self.keyring.keys():
            key_data = key_dict[key]
            miner_uid = key_data["uid"]
            if miner_uid in uids:
                if miner_uid == vali_uid:
                    continue
                index = uids.index(miner_uid)
                weights[index] = max_value - weights[index]
            else:
                weights.append(max_value)
        return uids, weights

    async def get_voter_keys(self, miners_dict: Dict) -> List:
        voter_keys = []
        balance_map = await self.manager.execute_query_map("balances")
        for key, data in miners_dict.items():
            if data["uid"] in balance_map:
                voter_keys.append(self.keyring[f"{key}.json"])
        return voter_keys

    async def vote(self):
        for subnet in CONFIG.subnets:
            if subnet in [1, 2]:
                continue
            try:
                miners_dict = await self.construct_miners_dict(subnet)
                vali_uid = await self.get_vali_uid(subnet)  # This is not an async function, so no await
                uids, weights = await self.construct_weights(subnet, vali_uid)
                voters = await self.get_voter_keys(miners_dict)
                logger.info(f"Subnet: {subnet}, UIDs: {uids}, Weights: {weights}, Voters: {voters}")
                # Implement voting logic here
            except Exception as e:
                logger.error(f"Error during voting for subnet {subnet}: {str(e)}")

async def main():
    voting_service = VotingService()
    await voting_service.vote()

if __name__ == "__main__":
    asyncio.run(main())