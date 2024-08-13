from dataclasses import dataclass, field
from loguru import logger
from fastapi import FastAPI
from pathlib import Path
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from communex.client import CommuneClient
from communex._common import get_node_url

# Initialize CommuneClient
comx = CommuneClient(get_node_url())

KEYSTORE_PATH = Path("./wallet/keystore")
if not KEYSTORE_PATH.exists():  
    KEYSTORE_PATH.mkdir(parents=True, exist_ok=True)

KEY_DICT_PATH = Path("./wallet/keystore/key_dict")
if not KEY_DICT_PATH.exists():
    KEY_DICT_PATH.parent.mkdir(parents=True, exist_ok=True)

QUERY_MAP_PATH = Path("./wallet/static/query_maps")
if not QUERY_MAP_PATH.exists():
    QUERY_MAP_PATH.mkdir(parents=True, exist_ok=True)

LOG_PATH = Path("./wallet/logs")
if not LOG_PATH.exists():
    LOG_PATH.mkdir(parents=True, exist_ok=True)

STATIC_PATH = Path("./wallet/static")
if not STATIC_PATH.exists():
    STATIC_PATH.mkdir(parents=True, exist_ok=True)

MINER_KEY_PATH = Path("wallet/raw_keys")
if not MINER_KEY_PATH.exists():
    MINER_KEY_PATH.mkdir(parents=True, exist_ok=True)

logger = logger.bind(name="data_models")
logger.info("Initializing data models...")
with open(f"{LOG_PATH}/data_models.log", "w", encoding="utf-8") as f:
    f.write("")
logger.add(sink="./wallet/logs/data_models.log", level="INFO")


HOST = "0.0.0.0"
PORT = 5500
RELOAD = True
SUBNETS = [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 17]
SUBNET_QUERY_LIST = [
    "query_map_key",
    "query_map_weights",
    "query_map_address"
]

# Initialize FastAPI app
app = FastAPI()

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5500", "http:100.71.164.114"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
if not Path("./wallet/templates").exists():
    raise ValueError("Templates directory not found. Please reinstall the application.")
# Initialize Jinja2 templates
templates = Jinja2Templates(directory="./wallet/templates")

app.mount("/static", StaticFiles(directory="./wallet/static"), name="static")

SUBNET_VALIDATORS = {
    "3": {
        "name": "fam",
        "key": "5FABzSh9BvHvNw8pnAwVQDwAMT2mM778njrC4aMDRJgqHmCy",
        "uid": 278,
    },
    "4": {
        "name": "fam",
        "key": "5FABzSh9BvHvNw8pnAwVQDwAMT2mM778njrC4aMDRJgqHmCy",
        "uid": 28,
    },
    "5": {
        "name": "fam",
        "key": "5FABzSh9BvHvNw8pnAwVQDwAMT2mM778njrC4aMDRJgqHmCy",
        "uid": 131,
    },
    "6": {
        "name": "fam",
        "key": "5FABzSh9BvHvNw8pnAwVQDwAMT2mM778njrC4aMDRJgqHmCy",
        "uid": 30,
    },
    "7": {
        "name": "fam",
        "key": "5FABzSh9BvHvNw8pnAwVQDwAMT2mM778njrC4aMDRJgqHmCy",
        "uid": 57,
    },
    "8": {
        "name": "fam",
        "key": "5FABzSh9BvHvNw8pnAwVQDwAMT2mM778njrC4aMDRJgqHmCy",
        "uid": 31,
    },
    "9": {
        "name": "fam",
        "key": "5FABzSh9BvHvNw8pnAwVQDwAMT2mM778njrC4aMDRJgqHmCy",
        "uid": 71,
    },
    "10": {
        "name": "commie3",
        "key": "5FABzSh9BvHvNw8pnAwVQDwAMT2mM778njrC4aMDRJgqHmCy",
        "uid": 66,
    },
    "11": {
        "name": "fam",
        "key": "5FABzSh9BvHvNw8pnAwVQDwAMT2mM778njrC4aMDRJgqHmCy",
        "uid": 18,
    },
    "12": {
        "name": "fam",
        "key": "5FABzSh9BvHvNw8pnAwVQDwAMT2mM778njrC4aMDRJgqHmCy",
        "uid": 9,
    },
    "13": {
        "name": "fam",
        "key": "5FABzSh9BvHvNw8pnAwVQDwAMT2mM778njrC4aMDRJgqHmCy",
        "uid": 18,
    },
    "14": {
        "name": "fam",
        "key": "5FABzSh9BvHvNw8pnAwVQDwAMT2mM778njrC4aMDRJgqHmCy",
        "uid": 249,
    },
    "15": {
        "name": "fam",
        "key": "5FABzSh9BvHvNw8pnAwVQDwAMT2mM778njrC4aMDRJgqHmCy",
        "uid": 309,
    },
    "16": {
        "name": "vali::comchat",
        "key": "5D4o6H19z6ctWjS9HzxBpMxqhuzCCCsgXk49AqXGPUqZEpRt",
        "uid": 1
    },
    "17": {
        "name": "fam",
        "key": "5FABzSh9BvHvNw8pnAwVQDwAMT2mM778njrC4aMDRJgqHmCy",
        "uid": 145,
    }    
}




@dataclass
class Configuration:
    host: field = field(default=HOST)
    port: field = field(default=PORT)
    reload: field = field(default=RELOAD)
    querymap_path: field = field(default=QUERY_MAP_PATH)
    log_path: field = field(default=LOG_PATH)
    static_path: field = field(default=STATIC_PATH)
    key_dict_path: field = field(default=KEY_DICT_PATH)
    miner_key_path: field = field(default=MINER_KEY_PATH)
    keystore_path: field = field(default=KEYSTORE_PATH)
    fastapi: field = field(default=app)
    jinja2_templates: field = field(default=templates)
    loguru_logger: field = field(default=logger)
    communex_client: field = field(default=comx)
    subnets: field = field(default_factory=list)
    subnet_query_list: field = field(default_factory=list)
    subnet_validators: field = field(default_factory=list)


class Settings(Configuration):
    def __init__(
        self,
        host=HOST,
        port=PORT,
        reload=RELOAD,
        querymap_path=QUERY_MAP_PATH,
        log_path=LOG_PATH,
        static_path=STATIC_PATH,
        key_dict_path=KEY_DICT_PATH,
        miner_key_path=MINER_KEY_PATH,
        keystore_path=KEYSTORE_PATH,
        fastapi=app,
        jinja2_templates=templates,
        loguru_logger=logger,
        communex_client=comx,
        subnets=SUBNETS,
        subnet_query_list=SUBNET_QUERY_LIST,
        subnet_validators=SUBNET_VALIDATORS
    ):
        super().__init__(self)
        self.host = host
        self.port = port
        self.reload = reload
        self.querymap_path = querymap_path
        self.log_path = log_path
        self.static_path = static_path
        self.key_dict_path = key_dict_path
        self.miner_key_path = miner_key_path
        self.keystore_path = keystore_path
        self.fastapi = fastapi
        self.jinja2_templates = jinja2_templates
        self.loguru_logger = loguru_logger
        self.communex_client = communex_client
        self.subnets = subnets
        self.subnet_query_list = subnet_query_list
        self.subnet_validators = subnet_validators


BT_RPC_METHODS = {
    "version": 0,
    "methods": [
        "account_nextIndex",
        "author_hasKey",
        "author_hasSessionKeys",
        "author_insertKey",
        "author_pendingExtrinsics",
        "author_removeExtrinsic",
        "author_rotateKeys",
        "author_submitAndWatchExtrinsic",
        "author_submitExtrinsic",
        "author_unwatchExtrinsic",
        "chainHead_unstable_body",
        "chainHead_unstable_call",
        "chainHead_unstable_follow",
        "chainHead_unstable_genesisHash",
        "chainHead_unstable_header",
        "chainHead_unstable_stopBody",
        "chainHead_unstable_stopCall",
        "chainHead_unstable_stopStorage",
        "chainHead_unstable_storage",
        "chainHead_unstable_unfollow",
        "chainHead_unstable_unpin",
        "chain_getBlock",
        "chain_getBlockHash",
        "chain_getFinalisedHead",
        "chain_getFinalizedHead",
        "chain_getHead",
        "chain_getHeader",
        "chain_getRuntimeVersion",
        "chain_subscribeAllHeads",
        "chain_subscribeFinalisedHeads",
        "chain_subscribeFinalizedHeads",
        "chain_subscribeNewHead",
        "chain_subscribeNewHeads",
        "chain_subscribeRuntimeVersion",
        "chain_unsubscribeAllHeads",
        "chain_unsubscribeFinalisedHeads",
        "chain_unsubscribeFinalizedHeads",
        "chain_unsubscribeNewHead",
        "chain_unsubscribeNewHeads",
        "chain_unsubscribeRuntimeVersion",
        "childstate_getKeys",
        "childstate_getKeysPaged",
        "childstate_getKeysPagedAt",
        "childstate_getStorage",
        "childstate_getStorageEntries",
        "childstate_getStorageHash",
        "childstate_getStorageSize",
        "delegateInfo_getDelegate",
        "delegateInfo_getDelegated",
        "delegateInfo_getDelegates",
        "neuronInfo_getNeuron",
        "neuronInfo_getNeuronLite",
        "neuronInfo_getNeurons",
        "neuronInfo_getNeuronsLite",
        "offchain_localStorageGet",
        "offchain_localStorageSet",
        "payment_queryFeeDetails",
        "payment_queryInfo",
        "state_call",
        "state_callAt",
        "state_getChildReadProof",
        "state_getKeys",
        "state_getKeysPaged",
        "state_getKeysPagedAt",
        "state_getMetadata",
        "state_getPairs",
        "state_getReadProof",
        "state_getRuntimeVersion",
        "state_getStorage",
        "state_getStorageAt",
        "state_getStorageHash",
        "state_getStorageHashAt",
        "state_getStorageSize",
        "state_getStorageSizeAt",
        "state_queryStorage",
        "state_queryStorageAt",
        "state_subscribeRuntimeVersion",
        "state_subscribeStorage",
        "state_traceBlock",
        "state_unsubscribeRuntimeVersion",
        "state_unsubscribeStorage",
        "subnetInfo_getLockCost",
        "subnetInfo_getSubnetHyperparams",
        "subnetInfo_getSubnetInfo",
        "subnetInfo_getSubnetsInfo",
        "subscribe_newHead",
        "system_accountNextIndex",
        "system_addLogFilter",
        "system_addReservedPeer",
        "system_chain",
        "system_chainType",
        "system_dryRun",
        "system_dryRunAt",
        "system_health",
        "system_localListenAddresses",
        "system_localPeerId",
        "system_name",
        "system_nodeRoles",
        "system_peers",
        "system_properties",
        "system_removeReservedPeer",
        "system_reservedPeers",
        "system_resetLogFilter",
        "system_syncState",
        "system_unstable_networkState",
        "system_version",
        "transaction_unstable_submitAndWatch",
        "transaction_unstable_unwatch",
        "unsubscribe_newHead",
    ],
}
