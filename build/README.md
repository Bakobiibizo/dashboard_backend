# Wallet

This is wallet interface for managing keyrings. Currently its being structued for interactions with the commune block chain but the future plan is to have it substrate chain agnostic with integrations for interacting with bitcoin, ethereum, solana, and olas. 

# Main Components

## Wallet

This is responsible for handling key interactions. It encrypts and decrypts individiual key files, a directory containing keyfiles as well as a single keyring object that contains a number of keys.
The keyring is saved in memory and the construction of the object is protected by a password that encodes and decodes the key_dict that is converted into the keyring.
The system is setup to accept keys saved in the commune format. 

```
{
    data: "{
            \"ss58_address\": \"5somekey\",
            \"public_key\": \"somepublickey\",
            \"private_key\": \"someprivatekey\",
            \"seed_hex\": \"someseedhex\",
            \"mnemonic\": \"some mnemonic phrase\",
            \"path\": \"path/to/keyfile\",
            \"derive_path"\: \"null\",
            \"ss58_format\": 42,
            \"crypto_type\": 1
        }",
}
```
Notice that the key object is a json string nested in a dictionary item with the name data. This is an artifact of the commune library implementation. 

the library extract the key and generate a keypair using the *private_key*, *public_key*, and *ss58_address*. 

We add both the key object and keypair to the keyring under the key *key_name*. 

```
keyring = 
    "some_keyname" :{
        "keypair": somekeypair, 
        "ss58_address": "5somekey",
        "public_key": "somepublickey",
        "private_key": "someprivatekey",
        "seed_hex": "someseedhex",
        "mnemonic": "some mnemonic phrase",
        "path": "path/to/keyfile",
        "derive_path\: "null",
        "ss58_format": 42,
        "crypto_type": 1
}
```

## ComxCommandManager

The command manager is responsible for make query requests and other communex commands. It parses the communex library path in your environment and extracts the functions. It uses a generic execute function to execute the commands directly. You can access the command list from the attribute *command_list* or a pretty version in *command_string*. The Command Manager will not execute commands that require a keypair with out entering the password directly into the getpass prompt directly on the machine but it can execute the query maps which are publicly available data. 
The other function it is in charge of is updating the query maps. They are the data objects that represent the different storage states on the chain. The wallet uses these maps as a source of data and caches a local copy for quick access asyncronously updating them every 3 minutes. This is a trade off for real time updated information and speed to retrieve data as the RPC calls to get the data tables have quiet a long call time. It will execute commands in a optimistic manner assuming the balances and other variables are correct from the user and returns the failed result if the transaction is not possible. 

# API

The api is what serves the HTMX front end templates. It also can execute query maps and non senstive commands. The front end does make requests to it for senstive commands but they will not function currently. I need to build out the authorization system for the front end but since the prototype is just a tear down it seems like the effort to build out the system would not be worth it till we are working on the final design. You can however run the commands from the terminal and I will have a cli tool built for that purpose. 

# TODO

- Build in the most common requests as explicit requetss for ease of use. 
- Enable a voting mechanic function
- Build a prompting cli tool
- Build out reports from the querymap data in csv format for consumption by the front end. 
- build out the reports page, and key management pages
- Build authentication so that users can use the front end gui to manage their keys
- Get the encryption audited
- Have the front end rebuilt in a more robust production format
- LICENSE
- Contribution guidlines
- ~~README~~

