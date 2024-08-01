import os
import hmac
import json
import uuid
import base64
import getpass
from pathlib import Path
from substrateinterface import Keypair
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from wallet.data_models import Settings
from wallet.encryption.custom_errors import EncryptionError

CONFIG = Settings()

logger = CONFIG.loguru_logger

logger.bind(name="wallet")

logger.info("Starting Wallet")

class Wallet:
    def __init__(self):
        self._keyring = {}
        self._encrypted_uuid = None
        self._verification_uuid = None
        self.keystore_path = Settings().key_dict_path

    @property
    def keyring(self):
        return self._keyring

    def encrypt_and_save_data(self, data, filepath):
        logger.info("Encrypting and saving data...")
        encrypted_data = self.encrypt_and_encode(data)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(json.dumps(encrypted_data))

    def decrypt_and_load_data(self, filepath):
        logger.info("Decrypting and loading data...")
        return self.decrypt_and_decode(Path(filepath).read_text("utf-8"))

    def get_encrypted_key_dict(self, key_path):
        logger.info("Getting encrypted key dict...")
        logger.debug(key_path)
        with open(key_path, "r", encoding="utf-8") as f:
            return json.loads(f.read())

    def load_keyring(self, key_dict):
        logger.info("Loading key_dict...")
        for key, values in key_dict.items():
            self._keyring[key] = Keypair(
                ss58_address=values["ss58_address"],
                public_key=values["public_key"],
                private_key=values["private_key"],
            )
        return self._keyring

    def verify_password(self):
        logger.info("Verifying password...")
        decrypted_uuid = self.decrypt_and_decode(self._encrypted_uuid)
        if decrypted_uuid == self._verification_uuid:
            return True
        else:
            return False

    def setup_verification(self, password_task, password):
        logger.info("Setting up verification...")
        self._verification_uuid = str(uuid.uuid4())
        self._encrypted_uuid = self.encrypt_and_encode(self._verification_uuid)

    def ask_for_password(self, password_task=None, setup=False):
        logger.info("Asking for password...")
        password = getpass.getpass("Password: ").encode("utf-8")
        
        if setup:
            confirm_password = getpass.getpass("Confirm password: ").encode("utf-8")
            if password != confirm_password:
                raise EncryptionError("Passwords do not match")
            self.setup_verification(password_task, password)
        return password_task(password) if password_task else password

    def encrypt_and_encode(self, unencrypted_data):
        logger.info("Encrypting data...")
        json_data = json.dumps(unencrypted_data)
        salt = os.urandom(16)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(), length=32, salt=salt, iterations=100000
        )
        key = base64.urlsafe_b64encode(self.ask_for_password(password_task=kdf.derive))
        f = Fernet(key)
        encrypted_data = f.encrypt(json_data.encode())
        return base64.b64encode(salt + encrypted_data).decode("utf-8")

    def decrypt_and_decode(self, encrypted_data):
        logger.info("Decrypting data...")
        decoded_data = base64.b64decode(encrypted_data.encode())
        salt, encrypted_data = decoded_data[:16], decoded_data[16:]
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(), length=32, salt=salt, iterations=100000
        )
        key = base64.urlsafe_b64encode(self.ask_for_password(password_task=kdf.derive))
        f = Fernet(key)
        decrypted_data = f.decrypt(encrypted_data).decode("utf-8")
        return json.loads(decrypted_data)

    def change_master_password(self, filepath=CONFIG.key_dict_path):
        logger.info("Changing master password...")
        if not self._keyring:
            raise ValueError("No key_dict loaded")

        current_key_dict = self.decrypt_and_load_data(filepath)
        self.encrypt_and_save_data(current_key_dict, filepath)
        

    def init_keyring(self, keypath=CONFIG.keystore_path):
        logger.info("Initializing key_dict...")
        encrypted_key_dict = self.get_encrypted_key_dict(keypath)
        decrypted_key_dict = self.decrypt_and_decode(encrypted_key_dict)
        self._keyring = self.load_keyring(decrypted_key_dict)
        

    def init_keydir(self, keydir=CONFIG.miner_key_path):
        logger.info("Initializing keydir...")
        keypath = CONFIG.keystore_path / "key_dict"
        key_dict = {}
        for filename in os.listdir(keydir):
            filepath = os.path.join(keydir, filename)
            logger.debug(filepath)
            with open(filepath, "r", encoding="utf-8") as f:
                file_content = json.loads(f.read())["data"]
                file_content = json.loads(file_content)
                key_dict[filename] = file_content
                key_dict[filename]["path"] = filepath
        self.encrypt_and_save_data(key_dict, keypath)   
        self.init_key_dict(keypath)


if __name__ == "__main__":
    wallet = Wallet()
    wallet.init_keydir(CONFIG.miner_key_path)
    unencrypted_data = wallet.decrypt_and_load_data(CONFIG.key_dict_path / "key_dict")