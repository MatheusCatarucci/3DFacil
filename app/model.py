import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_PATH = BASE_DIR / "data" / "business.db"


def buscar_usuario_por_email(email: str):
    conexao = sqlite3.connect(DATABASE_PATH)
    conexao.row_factory = sqlite3.Row

    try:
        cursor = conexao.cursor()

        cursor.execute("""
            SELECT id, name, email, password_hash
            FROM users
            WHERE email = ?
        """, (email,))

        usuario = cursor.fetchone()

        # --- DEBUG (comentado) ---
        # if usuario:
        #     print(f"Email no banco: {usuario['email']}")
        #     print(f"ID do usuário: {usuario['id']}")
        #     print(f"Nome: {usuario['name']}")
        #     print(f"Hash encontrado: {usuario['password_hash']}")
        # else:
        #     print("Nenhum usuário encontrado.")
        # -------------------------

        return dict(usuario) if usuario else None

    finally:
        conexao.close()