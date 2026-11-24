import sys
from pathlib import Path

# Permite importar o pacote "app" ao rodar o script da raiz do projeto
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import config  # noqa: E402
from app.database import db, init_db  # noqa: E402


def main() -> None:
    init_db()

    with db() as conn:
        tabelas = conn.execute(
            "SELECT name FROM sqlite_master "
            "WHERE type = 'table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
        ).fetchall()
        views = conn.execute(
            "SELECT name FROM sqlite_master WHERE type = 'view' ORDER BY name"
        ).fetchall()

    print(f"Banco: {config.DATABASE_PATH}")
    print(f"\n{len(tabelas)} tabelas:")
    for t in tabelas:
        print(f"  - {t['name']}")
    print(f"\n{len(views)} views:")
    for v in views:
        print(f"  - {v['name']}")


if __name__ == "__main__":
    main()