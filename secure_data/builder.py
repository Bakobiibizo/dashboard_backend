import base64
import os
from substrateinterface import Keypair
from nacl import utils, pwhash, secret


def generate_keypair():
    keypair = Keypair.create_from_uri(f"//{utils.random(32).hex()}")
    return keypair


def encrypt_data(data, public_key):
    shared_key = utils.random(secret.SecretBox.KEY_SIZE)
    box = secret.SecretBox(shared_key)
    encrypted = box.encrypt(data.encode())

    recipient_key = public_key.encode()
    encrypted_shared_key = secret.Box(
        utils.random(secret.Box.KEY_SIZE), recipient_key
    ).encrypt(shared_key)

    return base64.b64encode(encrypted + encrypted_shared_key).decode()


def create_self_decrypting_script(encrypted_data, command):
    script = f"""
import base64
import getpass
from nacl import pwhash, secret, utils

encrypted_data = "{encrypted_data}"
command = "{command}"

def decrypt_data(encrypted_data, password):
    decoded = base64.b64decode(encrypted_data)
    encrypted = decoded[:-80]
    encrypted_shared_key = decoded[-80:]
    
    salt = utils.random(pwhash.argon2i.SALTBYTES)
    private_key = pwhash.argon2i.kdf(secret.Box.KEY_SIZE, password.encode(), salt)
    
    shared_key = secret.Box(private_key).decrypt(encrypted_shared_key)
    box = secret.SecretBox(shared_key)
    return box.decrypt(encrypted).decode()

password = getpass.getpass("Enter decryption password: ")
decrypted_data = decrypt_data(encrypted_data, password)

with open("decrypted_data.txt", "w") as f:
    f.write(decrypted_data)

import subprocess
subprocess.run(command.split() + ["decrypted_data.txt"])
os.remove("decrypted_data.txt")
"""
    return script


# Main script
keypair = generate_keypair()
public_key = keypair.public_key
private_key = keypair.private_key
ss58_address = keypair.ss58_address

print(f"Public Key (SS58 format, type 42): {ss58_address}")
print(f"Private Key (keep this secret!): {private_key.hex()}")

data = input("Enter the path to encrypt: ")
command = "python self_decrypting_script.py"

encrypted_data = encrypt_data(data, public_key)
self_decrypting_script = create_self_decrypting_script(encrypted_data, command)

with open("self_decrypting_script.py", "w") as f:
    f.write(self_decrypting_script)

print("Self-decrypting script has been saved as 'self_decrypting_script.py'")
