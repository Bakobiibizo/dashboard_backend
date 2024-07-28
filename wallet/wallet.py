import json
import base64
import os
import base64
from loguru import logger
from getpass import getpass
from dotenv import load_dotenv
from pathlib import Path

from substrateinterface import Keypair
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from wallet.custom_errors import (
    KeyNotFoundError,
    IncorrectKeyError,
    CryptographyError,
    DecryptionError,
    EncryptionError,
    WrongPasswordError,
)


load_dotenv()


class Wallet:
    def __init__(self):
        self.keyring = {}

    def encrypt_and_encode(self, unencrypted_data):
        try:
            # Get the password
            passwd = getpass("Password: ")

            # Convert data to JSON string
            json_data = json.dumps(unencrypted_data)

            # Derive a key from the password
            salt = os.urandom(16)
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(passwd.encode()))

            # Encrypt the data
            f = Fernet(key)
            encrypted_data = f.encrypt(json_data.encode())

            return base64.b64encode(salt + encrypted_data).decode("utf-8")
        except (
            KeyError,
            IncorrectKeyError,
            KeyNotFoundError,
            WrongPasswordError,
            DecryptionError,
            EncryptionError,
            ValueError,
        ) as e:
            logger.error(f"Failed to encrypt data: {e}")
            raise CryptographyError(f"Failed to encrypt data: {e}") from e

    def decrypt_and_decode(self, encrypted_data: str) -> str:
        try:
            # Get the password
            passwd = getpass("Password: ")
            # Decode the base64 data
            decoded_data = base64.b64decode(encrypted_data.encode())

            # Extract salt and encrypted data
            salt, encrypted_data = decoded_data[:16], decoded_data[16:]

            # Derive the key from the password
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(passwd.encode()))

            # Decrypt the data
            f = Fernet(key)
            decrypted_data = f.decrypt(encrypted_data).decode("utf-8")
            return json.loads(decrypted_data)
        except (
            KeyError,
            IncorrectKeyError,
            KeyNotFoundError,
            WrongPasswordError,
            DecryptionError,
            EncryptionError,
            ValueError,
        ) as e:
            logger.error(f"Failed to decrypt data: {e}")
            raise CryptographyError(f"Failed to decrypt data: {e}") from e

    def get_local_keykeyring(self, key_dict: dict) -> Keypair:
        key_dict = key_dict or Path(key_dict).expanduser().read_text("utf-8")
        keyring = {}
        try:
            if '"data":' in key_dict:
                key_dict = json.loads(key_dict)["data"]
                key_dict = json.loads(key_dict)
            for key, values in key_dict.items():
                keyring[key] = Keypair(
                    ss58_address=values["key"],
                    public_key=values["public_key"],
                    private_key=values["private_key"],
                )
            self.keyring = keyring
            return keyring
        except Exception as e:
            logger.error(f"Failed to generate keypair: {e}")
            raise KeyNotFoundError(f"Failed to generate keypair: {e}") from e

    def encrypt_and_save_data(self, data):
        try:
            encrypted_data = self.encrypt_and_encode(data)
            with open("keyring", "w", encoding="utf-8") as f:
                f.write(encrypted_data)
        except Exception as e:
            logger.error(f"Failed to save keyring: {e}")
            raise KeyNotFoundError(f"Failed to save keyring: {e}") from e

    def decrypt_and_load_data(self, filepath="./key_store/keyring"):
        try:
            return self.decrypt_and_decode(Path(keyring).read_text("utf-8"))
        except Exception as e:
            logger.error(f"Failed to load keyring: {e}")
            raise KeyNotFoundError(f"Failed to load keyring: {e}") from e

    def get_key_dict(self, key_path: str):
        try:
            with open(key_path, "r", encoding="utf-8") as f:
                return json.loads(f.read())
        except FileNotFoundError as e:
            logger.error(f"Key file not found: {e}")
            raise KeyNotFoundError(f"Key file not found: {e}") from e
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode JSON: {e}")
            raise DecryptionError(f"Failed to decode JSON: {e}") from e
        except Exception as e:
            logger.error(f"Failed to load key file: {e}")
            raise KeyNotFoundError(f"Failed to load key file: {e}") from e


def test():
    wallet = Wallet()

    secret_data = "Sup3r$ecretD@ta"
    encrypted_data = wallet.encrypt_and_encode(secret_data)
    print(encrypted_data)

    save_path = Path("wallet/key_store.json")
    save_path.write_text(json.dumps(encrypted_data), encoding="utf-8")

    b64_data = save_path.read_text("utf-8")
    unecrypted_data = wallet.decrypt_and_decode(b64_data)
    print(unecrypted_data)


if __name__ == "__main__":
    test()
