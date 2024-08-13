import asyncio
import json
from typing import Dict, List
from wallet.encryption.wallet import Wallet
from wallet.commands.comx_command_manager import ComxCommandManager
from wallet.data_models import Settings

CONFIG = Settings()
logger = CONFIG.loguru_logger.bind(name="register_service")

class RegisterService:
    def __init__(self):
        self.manager = ComxCommandManager()
        self.wallet = Wallet()
        self.wallet.init_keyring(CONFIG.key_dict_path)

    async def get_miner_keys(self) -> Dict[str, Dict[str, str]]:
        miner_keys = {}
        keypaths = CONFIG.miner_key_path.iterdir()
        for keypath in keypaths:
            json_key = json.loads(keypath.read_text("utf-8"))["data"]
            key = json.loads(json_key)
            miner_data = {"name": key["path"], "key": key["ss58_address"]}
            miner_keys[miner_data["name"]] = miner_data
        return miner_keys

    async def register(self, name: str, keyname: str, ip: str, port: int, subnet: int) -> Dict:
        logger.info(f"Registering {name} on subnet {subnet}")
        address = f"{ip}:{port}"
        try:
            result = await self.manager.comx.register_module(
                key=self.wallet.keyring[f"{name}".json],
                address=address,
                subnet=subnet
                )
            if result.is_success:
                logger.info(f"Successfully registered {name} on subnet {subnet}")
                return result.extrinsic
            else:
                logger.error(f"Failed to register {name} on subnet {subnet}: {result.error}")
                return {"error": result.error}
        except Exception as e:
            logger.error(f"Error registering {name} on subnet {subnet}: {str(e)}")
            return {"error": str(e)}

    async def bulk_register(self, miner_keys: Dict[str, Dict[str, str]]) -> List[Dict]:
        results = []
        for subnet in CONFIG.subnets:
            for i, (key, data) in enumerate(miner_keys.items()):
                result = await self.register(key, data['name'], "127.0.0.1", 8000 + i, subnet)
                results.append({
                    "key": key,
                    "subnet": subnet,
                    "result": result
                })
        return results

    async def fund_keys(self, funding_key: str, key_names: List[str], amount: float) -> List[Dict]:
        results = []
        for key in key_names:
            try:
                result = await self.manager.execute_command(
                    "transfer",
                    key=funding_key,
                    amount=amount,
                    dest=key
                )
                results.append({
                    "key": key,
                    "amount": amount,
                    "result": result
                })
            except Exception as e:
                logger.error(f"Error funding key {key}: {str(e)}")
                results.append({
                    "key": key,
                    "amount": amount,
                    "error": str(e)
                })
        return results

async def main():
    register_service = RegisterService()
    await register_service.manager.init_manager()
    
    miner_keys = await register_service.get_miner_keys()
    registration_results = await register_service.bulk_register(miner_keys)
    logger.info(f"Registration results: {registration_results}")

    funding_key = "vali::eden00"
    amount_to_fund = 200.0  # Adjust as needed
    funding_results = await register_service.fund_keys(funding_key, list(miner_keys.keys()), amount_to_fund)
    logger.info(f"Funding results: {funding_results}")

if __name__ == "__main__":
    asyncio.run(main())