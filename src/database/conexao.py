#src/database/conexao.py
from dotenv import load_dotenv
import os
from firebird.driver import connect

# Força o carregamento do .env correto a partir da raiz do projeto
dotenv_path = os.path.join(os.path.dirname(__file__), '.', '.', '.env')
load_dotenv(dotenv_path)

print("[DEBUG] DSN carregado do .env:", os.getenv("FIREBIRD_DSN"))


def conectar():
    try:
        con = connect(
            database=os.getenv("FIREBIRD_DSN"),  # Aqui o nome correto é 'database'
            user=os.getenv("FIREBIRD_USER"),
            password=os.getenv("FIREBIRD_PASSWORD"),
        )
        print("[DEBUG] Conectando ao banco:", os.getenv("FIREBIRD_DSN"))
        print("[OK] Conectado ao banco Firebird com sucesso.")
        return con
    except Exception as e:
        print("[ERRO] Falha na conexão com o Firebird:", e)
        return None

#Temporariamente desativado para evitar erro de conexão com o novo banco
#Verificar possibilidade de usar novo modelo de database compatível, como MySql, SQLite ou PostgreSQL

# def conectar_novo_banco():
#     try:
#         # Imprimir o caminho sendo utilizado para depuração
#         db_path = os.getenv("FIREBIRD_NEW_DSN")
#         print(f"[DEBUG] Tentando conectar ao banco: {db_path}")
#         con = connect(
#             database=db_path,
#             user=os.getenv("FIREBIRD_USER"),
#             password=os.getenv("FIREBIRD_PASSWORD"),
#         )
#         print("[OK] Conectado ao novo banco de dados com sucesso.")
#         return con
#     except Exception as e:
#         print("[ERRO] Falha na conexão com o novo banco:", e)
#         # Adicione verificações específicas para diagnóstico
#         if not os.getenv("FIREBIRD_NEW_DSN"):
#             print("[ERRO] Variável FIREBIRD_NEW_DSN não encontrada no arquivo .env")
#         return None
