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

KEYRING_PATH = Path("./wallet/keystore/keyring")
if KEYRING_PATH.exists():
    KEYRING_PATH.mkdir(parents=True, exist_ok=True)

QUERY_MAP_PATH = Path("./wallet/static/query_maps")
if not QUERY_MAP_PATH.exists():
    QUERY_MAP_PATH.mkdir(parents=True, exist_ok=True)

LOG_PATH = Path("./wallet/logs")
if not LOG_PATH.exists():
    LOG_PATH.mkdir(parents=True, exist_ok=True)

STATIC_PATH = Path("./wallet/static")
if not STATIC_PATH.exists():
    STATIC_PATH.mkdir(parents=True, exist_ok=True)


logger = logger.bind(name="data_models")
logger.info("Initializing data models...")
with open(f"{LOG_PATH}/data_models.log", "w", encoding="utf-8") as f:
    f.write("")
logger.add(sink="./wallet/logs/data_models.log", level="INFO")

HOST = "0.0.0.0"
PORT = 5500
RELOAD = True

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


@dataclass
class Configuration:
    host: field = field(default=HOST)
    port: field = field(default=PORT)
    reload: field = field(default=RELOAD)
    querymap_path: field = field(default=QUERY_MAP_PATH)
    log_path: field = field(default=LOG_PATH)
    static_path: field = field(default=STATIC_PATH)
    keyring_path: field = field(default=KEYRING_PATH)
    fastapi: field = field(default=app)
    jinja2_templates: field = field(default=templates)
    loguru_logger: field = field(default=logger)
    communex_client: field = field(default=comx)


class Settings(Configuration):
    def __init__(
        self,
        host=HOST,
        port=PORT,
        reload=RELOAD,
        querymap_path=QUERY_MAP_PATH,
        log_path=LOG_PATH,
        static_path=STATIC_PATH,
        keyring_path=KEYRING_PATH,
        fastapi=app,
        jinja2_templates=templates,
        loguru_logger=logger,
        communex_client=comx,
    ):
        super().__init__(self)
        self.host = host
        self.port = port
        self.reload = reload
        self.querymap_path = querymap_path
        self.log_path = log_path
        self.static_path = static_path
        self.keyring_path = keyring_path
        self.fastapi = fastapi
        self.jinja2_templates = jinja2_templates
        self.loguru_logger = loguru_logger
        self.communex_client = communex_client