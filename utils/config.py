# utils/config.py
import os
from dotenv import load_dotenv

# Load .env from project root
load_dotenv()

def _env(name: str, default: str | None = None, required: bool = False) -> str:
    v = os.getenv(name, default)
    if required and (v is None or str(v).strip() == ""):
        raise RuntimeError(f"Missing required environment variable: {name}")
    return v

# Base host from .env (no trailing slash)
_BASE_HOST = _env("BASE_URL", required=True).rstrip("/")

# OrangeHRM login path
_LOGIN_PATH = "/web/index.php/auth/login"

# Exported config vars used by tests
BASE_URL = f"{_BASE_HOST}{_LOGIN_PATH}"     # -> full login URL
USERNAME = _env("HRM_USERNAME", required=True)
PASSWORD = _env("HRM_PASSWORD", required=True)
DEFAULT_WAIT = int(_env("DEFAULT_WAIT", "20"))
