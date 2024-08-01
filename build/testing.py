from wallet.commands.register import bulk_register
from wallet.encryption.wallet import Wallet
from wallet.data_models import Settings

CONFIG = Settings()

wallet = Wallet()

wallet.init_key_dict(CONFIG.key_dict_path)


bulk_register()