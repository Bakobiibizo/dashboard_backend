from wallet.commands.comx_command_manager import ComxCommandManager
from wallet.encryption.wallet import Wallet
from wallet.data_models import Settings

manager = ComxCommandManager()
wallet = Wallet()

CONFIG = Settings()

def transfer(funding_key, amount, target_key):
    wallet.init_keyring(CONFIG.key_dict_path)
    target = wallet.keyring[f"{target_key}.json"].ss58_address
    print(target)
    print(wallet.keyring)
    keypair = wallet.keyring[f"{funding_key}.json"]
    result = manager.get_commands_dict()["transfer"](keypair, amount, target)
    if result.is_success:
        return result.extrinsic
    else:
        print(result.error)
    



print(transfer(funding_key="vali::eden00", amount=200, target_key="tigerking::0"))