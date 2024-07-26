from substrateinterface import Keypair, KeypairType
from substrateinterface.utils.ss58 import ss58_encode
import hashlib
import json

# Function to create a multi-sig account
def create_multi_sig(signatories, threshold):
    # Sort the public keys
    sorted_pubkeys = sorted(signatories)
    
    # Prepare the data for hashing
    data = bytes([0x00])  # Prefix for multi-sig account
    data += bytes([len(sorted_pubkeys)])  # Number of signatories
    data += bytes([threshold])  # Threshold
    
    for pubkey in sorted_pubkeys:
        data += bytes.fromhex(pubkey)
    
    # Hash the data
    return hashlib.blake2b(data, digest_size=32).digest()

# Generate some example keypairs
keypair1 = Keypair.create_from_uri('//Alice')
keypair2 = Keypair.create_from_uri('//Bob')
keypair3 = Keypair.create_from_uri('//Charlie')

# Get the public keys
pubkey1 = keypair1.public_key
pubkey2 = keypair2.public_key
pubkey3 = keypair3.public_key

# Create the multi-sig account (2 out of 3 in this example)
signatories = [pubkey1.hex(), pubkey2.hex(), pubkey3.hex()]
threshold = 2
multi_sig_account = create_multi_sig(signatories, threshold)

# Encode the multi-sig account in SS58 format
# Note: 42 is the default network ID for Substrate, adjust as needed for your specific chain
ss58_address = ss58_encode(multi_sig_account, ss58_format=42)

print(f"Multi-signature SS58 address: {ss58_address}")

# Print individual public keys for reference
print("\nIndividual public keys:")
print(f"Alice: {keypair1.ss58_address}")
print(f"Bob: {keypair2.ss58_address}")
print(f"Charlie: {keypair3.ss58_address}")