import os
import sys
import hmac
import json
import uuid
import ctypes
import base64
import getpass
import ctypes.wintypes
from pathlib import Path
from loguru import logger
from substrateinterface import Keypair
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from encryption.custom_errors import (
    KeyNotFoundError,
    IncorrectKeyError,
    CryptographyError,
    DecryptionError,
    EncryptionError,
    WrongPasswordError,
)


class Wallet:
    def __init__(self):
        self._keyring = {}
        self._encrypted_uuid = None
        self._verification_uuid = None

    @property
    def keyring(self):
        return self._keyring

    def _secure_string(self, string):
        buf = ctypes.create_string_buffer(string) if isinstance(string, str) else string

        if sys.platform == "win32":
            ctypes.windll.kernel32.VirtualLock(ctypes.byref(buf), ctypes.sizeof(buf))
        else:
            ctypes.CDLL("libc.so.6").mlock(ctypes.byref(buf), ctypes.sizeof(buf))

        return buf

    def _clear_string(self, string):
        ctypes.memset(ctypes.cast(string, ctypes.c_void_p).value, 0, len(string))

    def setup_verification(self, password_task, password):
        self._verification_uuid = str(uuid.uuid4())
        self._encrypted_uuid = password_task(password)

    def verify_password(self):
        try:
            if not self._encrypted_uuid or not self._verification_uuid:
                raise EncryptionError("Missing encrypted uuid or verification uuid")
            decrypted_uuid = self._secure_string(
                self.decrypt_and_decode(self._verification_uuid)
            )
            if decrypted_uuid == self._verification_uuid:
                return hmac.compare_digest(decrypted_uuid.raw, self._verification_uuid.encode("utf-8"))
        except (
            KeyNotFoundError,
            IncorrectKeyError,
            CryptographyError,
            DecryptionError,
        ):
            logger.error("Failed to decrypt verification uuid")
            raise EncryptionError("Failed to decrypt verification uuid") from None
        finally:
            if "decrypted_uuid" in locals():
                self._clear_string(decrypted_uuid)

    def ask_for_password(self, password_task=None, setup=False):
        password = self._secure_string(getpass.getpass("Password: ").encode("utf-8"))
        try:
            if setup:
                check = self._secure_string(
                    getpass.getpass("Confirm password: ").encode("utf-8")
                )
                if password != check:
                    self._clear_string(check)
                    raise EncryptionError("Passwords do not match") from None
                self.setup_verification(password_task, password)
            return password_task(password) if password_task else password.raw
        finally:
            if "password" in locals():
                self._clear_string(password.raw)
            if "check" in locals():
                self._clear_string(check.raw)

    def encrypt_and_encode(self, unencrypted_data, setup=False):
        try:
            # Convert data to JSON string
            json_data = self._secure_string(json.dumps(unencrypted_data))

            # Derive a key from the password
            salt = os.urandom(16)
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = self._secure_string(
                base64.urlsafe_b64encode(
                    self.ask_for_password(password_task=kdf.derive, setup=setup)
                )
            )

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
        finally:
            if "json_data" in locals():
                self._clear_string(json_data.raw)
            if "key" in locals():
                self._clear_string(key.raw)

    def decrypt_and_decode(self, encrypted_data: str, setup=False):
        try:
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
            key = self._secure_string(
                base64.urlsafe_b64encode(
                    self.ask_for_password(password_task=kdf.derive, setup=setup)
                )
            )

            # Decrypt the data
            f = Fernet(key.raw)
            decrypted_data = self._secure_string(
                f.decrypt(encrypted_data).decode("utf-8")
            )
            return json.loads(decrypted_data.raw)

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
        finally:
            if "key" in locals():
                self._clear_string(key.raw)
            if "json_data" in locals():
                self._clear_string(decrypted_data.raw)

    def keyring_from_key_dict(self, key_dict) -> Keypair:
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

    def encrypt_and_save_data(self, data, filepath="./keystore/key_dict", setup=False):
        try:
            encrypted_data = self.encrypt_and_encode(data, setup=setup)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(encrypted_data)
        except Exception as e:
            logger.error(f"Failed to save keyring: {e}")
            raise KeyNotFoundError(f"Failed to save keyring: {e}") from e

    def decrypt_and_load_data(self, filepath="./keystore/key_dict", setup=False):
        try:
            return self.decrypt_and_decode(
                Path(filepath).read_text("utf-8"), setup=setup
            )
        except Exception as e:
            logger.error(f"Failed to load keyring: {e}")
            raise KeyNotFoundError(f"Failed to load keyring: {e}") from e

    def get_encrypted_key_dict(self, key_path: str):
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

    def init_keyring(self, keypath="keystore/keyring"):
        try:
            key_dict = self.decrypt_and_load_data(keypath, setup=True)
            return self.keyring_from_key_dict(key_dict)
        except (
            KeyNotFoundError,
            IncorrectKeyError,
            CryptographyError,
            DecryptionError,
            EncryptionError,
            WrongPasswordError,
        ) as e:
            logger.error(f"Failed to load keys: {e}")
            raise KeyNotFoundError(f"Failed to load keys: {e}") from e
        except Exception as e:
            logger.error(f"Failed to load keys: {e}")
            raise KeyError(f"Failed to load keys: {e}") from e

    def change_master_password(self, filepath="keystore/key_dict"):
        try:
            if not self._keyring:
                raise ValueError("No keyring loaded")

            # Decrypt the current key_dict
            current_key_dict = self._secure_string(self.decrypt_and_load_data(filepath))

            # Encrypt with a new password
            self.encrypt_and_save_data(current_key_dict, filepath, setup=True)

            logger.info("Checking password")
            if self.verify_password():
                logger.info("Master password changed successfully")
            else:
                logger.error("Please retry")
        except (KeyNotFoundError, IncorrectKeyError, CryptographyError) as e:
            logger.error(f"Failed to load keys: {e}")
            raise KeyNotFoundError(f"Failed to load keys: {e}") from e
        except Exception as e:
            logger.error(f"Failed to load keys: {e}")
            raise KeyError(f"Failed to load keys: {e}") from e
        finally:
            if "current_key_dict" in locals():
                self._clear_string(current_key_dict)

        return True
