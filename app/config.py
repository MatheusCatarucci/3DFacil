import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.getenv("SECRET_KEY", "")
if not SECRET_KEY or SECRET_KEY == "COLE_AQUI_A_CHAVE_GERADA":
    raise RuntimeError(
        "SECRET_KEY não configurada. Edite o arquivo .env e informe uma chave."
    )

DATABASE_PATH = BASE_DIR / os.getenv("DATABASE_PATH", "data/business.db")
APP_ENV = os.getenv("APP_ENV", "development")