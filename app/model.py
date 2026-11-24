from pathlib import Path
import sqlite3

BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_PATH = BASE_DIR / "data" / "business.db"

def buscar_usuario_por_email(email:str):
    conexao = sqlite3.connect(DATABASE_PATH)
    conexao.row_factory = sqlite3.Row
    
    try:
        cursor = conexao.cursor()
        
        cursor.execute(
            "SELECT * FROM usuarios WHERE email = ?;",
            (email,)
        )
        
        usuario = cursor.fetchone()
        
        return dict(usuario) if usuario else None
    
    finally:
        conexao.close()