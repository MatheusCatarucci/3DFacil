import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

DATABASE_PATH = BASE_DIR / os.getenv(
    "DATABASE_PATH",
    "data/business.db"
)