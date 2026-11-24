import sqlite3
import sys
from getpass import getpass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import bcrypt  # noqa: E402

from app.database import db  # noqa: E402


def main() -> None:
    print("Criar usuário administrador\n")

    nome = input("Nome: ").strip()
    email = input("E-mail: ").strip().lower()
    senha = getpass("Senha (mínimo 8 caracteres): ")
    confirmacao = getpass("Confirme a senha: ")

    if not nome or not email:
        sys.exit("Nome e e-mail são obrigatórios.")
    if len(senha) < 8:
        sys.exit("A senha precisa ter pelo menos 8 caracteres.")
    if senha != confirmacao:
        sys.exit("As senhas não conferem.")
    if len(senha.encode("utf-8")) > 72:
        sys.exit("A senha é longa demais (limite de 72 bytes do bcrypt).")

    senha_hash = bcrypt.hashpw(senha.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    try:
        with db() as conn:
            conn.execute(
                "INSERT INTO users (name, email, password_hash, role) "
                "VALUES (?, ?, ?, 'admin')",
                (nome, email, senha_hash),
            )
    except sqlite3.IntegrityError:
        sys.exit("Já existe um usuário com esse e-mail.")

    print(f"\nAdministrador '{nome}' criado com sucesso.")


if __name__ == "__main__":
    main()