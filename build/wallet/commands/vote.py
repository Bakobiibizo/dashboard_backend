from wallet.commands.comx_command_manager import ComxCommandManager
from wallet.encryption.wallet import Wallet
from wallet.data_models import Settings

CONFIG = Settings()

manager = ComxCommandManager()
wallet = Wallet()

keyring = wallet.keyring

print(keyring)

def vote(key, subnet):
    data_maps = manager.load_data_maps(CONFIG.querymap_path)
    weights = data_maps.read_text("utf-8")[subnet]["query_map_weights"]
    print(weights)