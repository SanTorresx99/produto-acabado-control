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

def conectar_novo_banco():
    try:
        # Altere o caminho para o novo banco de dados
        con = connect(
            database=os.getenv("FIREBIRD_NEW_DSN"),  # Nome do novo banco
            user=os.getenv("FIREBIRD_USER"),
            password=os.getenv("FIREBIRD_PASSWORD"),
        )
        print("[OK] Conectado ao novo banco de dados com sucesso.")
        return con
    except Exception as e:
        print("[ERRO] Falha na conexão com o novo banco:", e)
        return None