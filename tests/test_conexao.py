import sys
import os

# Adiciona o caminho da pasta 'src' ao sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

# Agora sim podemos importar do módulo correto
from database.conexao import conectar

def test_conexao_firebird():
    conn = conectar()
    if conn:
        print("Conexão realizada com sucesso!")
        conn.close()
    else:
        print("Erro na conexão.")

if __name__ == "__main__":
    test_conexao_firebird()
