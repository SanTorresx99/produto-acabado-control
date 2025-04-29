from database.conexao import conectar
import pandas as pd

def autenticar_usuario(login, senha):
    """
    Autentica o usuário com base no login e senha fornecidos.
    Verifica se o usuário existe no banco de dados e se a senha está correta.

    Parâmetros:
        login (str): O login do usuário.
        senha (str): A senha do usuário.

    Retorna:
        bool: Retorna True se a autenticação for bem-sucedida, caso contrário False.
    """
    conn = conectar()  # Usando a conexão com o banco correto (MENTOR ou CONTROLE_PA)
    if not conn:
        return False

    try:
        sql = f"""
        SELECT * FROM USUARIOS WHERE LOGIN = '{login}' AND SENHA = {senha} AND ATIVO = 'S'
        """
        df = pd.read_sql(sql, conn)
        if not df.empty:
            print(f"[OK] Usuário {login} autenticado com sucesso!")
            return True
        else:
            print("[ERRO] Usuário ou senha inválidos.")
            return False
    except Exception as e:
        print(f"[ERRO] Falha ao autenticar usuário: {e}")
        return False
    finally:
        conn.close()