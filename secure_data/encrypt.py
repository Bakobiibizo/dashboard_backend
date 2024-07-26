import json
import base64
from dataclasses import dataclass
from substrateinterface import Keypair, KeypairType
from cryptography.fernet import Fernet

@dataclass
class KeyConfig:
    ss58_address: str = None,
    public_key: bytes | str = None,
    private_key: bytes | str = None,
    ss58_format: int = None,
    seed_hex: str | bytes = None,
    crypto_type: int = KeypairType.SR25519
    

class Wallet:
    def __init__(self):
        self.keypair = Keypair
        self.keyring = {}
        
    def create_keypair(self, password: str):
        keypair = Keypair.create_from_seed(password)
        
        private_key = keypair.private_key
        public_key = keypair.public_key
        ss58_address = keypair.ss58_address
        
        encoded_key = self.encode_with_password(password, private_key)
        self.keyring[ss58_address] = {
            "ss58_address": ss58_address,
            "public_key": public_key,
            "private_key": encoded_key
        }
        
        with open("data/keyring.json", "w", encoding="utf-8") as f:
            json.dump(self.keyring, f, indent=4)
            
        return keypair
    
    def create_seed_hex(self, password: str):
        password = base64.b64encode(password.encode("utf-8"))[:32].hex()
        print(password)
        return password
    
    def encode_with_password(self, password: str, data):
        encoded_data = base64.b64encode(data)
        return Fernet(password).encrypt(encoded_data)
    
    def decode_with_password(self, password: str, data):
        encoded_data = Fernet(password).decrypt(data)
        return base64.b64decode(encoded_data)
    
    
if __name__ == "__main__":
    wallet = Wallet()
    keypair = wallet.create_keypair("password")
    print(keypair)