import json
import base64
import os
from getpass import getpass
from dotenv import load_dotenv
from pathlib import Path
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


load_dotenv()


def encrypt_and_encode(data, password):
    # Convert data to JSON string
    json_data = json.dumps(data)

    # Derive a key from the password
    salt = os.urandom(16)
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))

    # Encrypt the data
    fern = Fernet(key)
    encrypted_data = fern.encrypt(json_data.encode())

    return base64.b64encode(salt + encrypted_data).decode("utf-8")


def create_keypair_decrypter():
    return """
def get_keypairs(password):
    keyring = unpack_and_decrypt(password)
    for key in keyring:
        key_data = json.loads(keyring[key])
        private_key = key_data["private_key"]
        public_key = key_data["public_key"]
        ss58key = key_data["ss58_address"]

        keypair = Keypair(ss58key, public_key, private_key)
        keyring[key] = keypair
    return keyring


if __name__ == "__main__":
    print(get_keypairs())"""


def create_unpacker(encrypted_data):
    return f"""
import os
import json
import base64
import subprocess
from getpass import getpass

command = "pip install cryptography python-dotenv substrate-interface"
subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

from substrateinterface import Keypair
from dotenv import load_dotenv
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

load_dotenv()


def unpack_and_decrypt(password):
    encrypted_data = "{encrypted_data}"
    
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
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    
    # Decrypt the data
    f = Fernet(key)
    decrypted_data = f.decrypt(encrypted_data)
    
    # Parse the JSON data
    return json.loads(decrypted_data)

{create_keypair_decrypter()}
"""


keyring = json.loads(
    Path("/home/bakobi/.commune/key/eden.Validator_1.json").read_text("utf-8")
)
password = getpass("Enter the password to unlock: ")

# Encrypt and encode the data
encrypted_encoded_data = encrypt_and_encode(keyring, password)

# Create the unpacker script
unpacker = create_unpacker(encrypted_encoded_data)

# Save the unpacker script to a file
with open("unpacker.py", "w", encoding="utf-8") as f:
    f.write(unpacker)

print("Unpacker script has been created as 'unpacker.py'")
