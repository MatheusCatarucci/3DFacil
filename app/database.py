import sqlite3
from contextlib import contextmanager
from pathlib import Path

from app import config

BASE_DIR = Path(__file__).resolve().parent.parent
SCHEMA_PATH = BASE_DIR / "sql" / "schema.sql"


def get_connection() -> sqlite3.Connection:
    """Abre uma conexão com as configurações corretas.

    foreign_keys precisa ser ativado em TODA conexão, senão o SQLite
    ignora as chaves estrangeiras.
    """
    config.DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(config.DATABASE_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA busy_timeout = 5000")
    return conn


@contextmanager
def db():
    """Uso:
        with db() as conn:
            conn.execute("INSERT ...")
    Faz commit ao sair do bloco e rollback se ocorrer erro.
    """
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def get_db():
    """Dependência do FastAPI:
        def rota(conn = Depends(get_db)): ...
    """
    with db() as conn:
        yield conn


def init_db() -> None:
    """Cria as tabelas, índices, views e triggers (seguro para rodar de novo)."""
    schema = SCHEMA_PATH.read_text(encoding="utf-8")
    with db() as conn:
        conn.executescript(schema)