from wallet.commands.comx_command_manager import ComxCommandManager
from wallet.encryption.wallet import Wallet
from wallet.data_models import Settings

CONFIG = Settings()

manager = ComxCommandManager()
wallet = Wallet()

keyring = wallet.keyring

print(keyring)

def vote(key, subnet):
    subnet_maps = manager.get_subnet_maps(subnet)
    weights = subnet_maps["weights"]
    
    
    print(weights)