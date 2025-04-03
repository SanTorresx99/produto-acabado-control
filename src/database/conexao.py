import os
from firebird.driver import connect
from dotenv import load_dotenv

load_dotenv()

def conectar():
    try:
        con = connect(
            database=os.getenv("FIREBIRD_DSN"),  # Aqui o nome correto é 'database'
            user=os.getenv("FIREBIRD_USER"),
            password=os.getenv("FIREBIRD_PASSWORD"),
        )
        print("[OK] Conectado ao banco Firebird com sucesso.")
        return con
    except Exception as e:
        print("[ERRO] Falha na conexão com o Firebird:", e)
        return None
