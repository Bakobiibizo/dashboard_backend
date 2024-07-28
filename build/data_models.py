
from loguru import logger
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from communex.client import CommuneClient
from communex._common import get_node_url
from substrateinterface import Keypair
from data.comx_command_manager import ComxCommandManager
from encryption.wallet import Wallet
from encryption.custom_errors import (
    KeyNotFoundError,
    IncorrectKeyError,
    CryptographyError,
    DecryptionError,
    EncryptionError,
    WrongPasswordError,
    InvalidKeyError,
    InvalidSaltError
)

logger = logger.bind(name="data_models")
logger.info("Initializing data models...")
logger.add(sink="logs/data_models.log", level="INFO")

manager = ComxCommandManager()

wallet = Wallet()

# Initialize FastAPI app
app = FastAPI()

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8000",
        "http:100.71.164.114"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize Jinja2 templates
templates = Jinja2Templates(directory="templates")

# Initialize CommuneClient
comx = CommuneClient(get_node_url())

__all__ = [
    "KeyNotFoundError",
    "IncorrectKeyError",
    "CryptographyError",
    "DecryptionError",
    "EncryptionError",
    "WrongPasswordError",
    "InvalidKeyError",
    "InvalidSaltError",
    "HTTPException",
    "Request",
    "app",
    "templates",
    "comx",
    "Keypair",
    "wallet",
    "logger",
    "manager"
] 