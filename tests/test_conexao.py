import sys
import os

# Adiciona o caminho da pasta 'src' ao sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from database.conexao import conectar, conectar_novo_banco

def test_conexoes_firebird():
    # Testa a conexão com o banco principal
    print("Testando conexão com o banco principal...")
    conn = conectar()
    if conn:
        print("[OK] Conexão com o banco principal realizada com sucesso!")
        conn.close()  # Fechar a conexão após o teste
    else:
        print("[ERRO] Falha na conexão com o banco principal.")

    # Testa a conexão com o novo banco
    print("\nTestando conexão com o novo banco...")
    conn_novo = conectar_novo_banco()
    if conn_novo:
        print("[OK] Conexão com o novo banco realizada com sucesso!")
        conn_novo.close()  # Fechar a conexão após o teste
    else:
        print("[ERRO] Falha na conexão com o novo banco.")

if __name__ == "__main__":
    test_conexoes_firebird()