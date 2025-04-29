import pandas as pd
import os

# Função para autenticar usuário
def autenticar_usuario(login, senha):
    """
    Função que autentica o usuário no sistema, verificando o login e senha no arquivo 'usuarios.csv'.

    Parâmetros:
        login (str): O login do usuário.
        senha (str): A senha do usuário.

    Retorna:
        dict: Dados do usuário (ID, login, nome, etc.) caso o login e senha estejam corretos, 
              ou None caso contrário.
    """
    usuarios_file = os.path.join(os.path.dirname(__file__), '..', 'files', 'usuarios.csv')

    try:
        # Lê o arquivo CSV com o separador correto (verifique se é ponto e vírgula)
        df_usuarios = pd.read_csv(usuarios_file, sep=',')
        
        # Remover espaços extras nas colunas
        df_usuarios.columns = df_usuarios.columns.str.strip()

        # Converte as colunas relevantes para string
        df_usuarios['LOGIN'] = df_usuarios['LOGIN'].astype(str).str.strip()
        df_usuarios['SENHA'] = df_usuarios['SENHA'].astype(str).str.strip()
        df_usuarios['ATIVO'] = df_usuarios['ATIVO'].astype(str).str.strip()

        # Imprime as colunas para depuração
        print("[INFO] Colunas carregadas:", df_usuarios.columns)

        # Verifica se o login e a senha existem no dataframe
        usuario = df_usuarios[(df_usuarios['LOGIN'] == login.strip()) &
                               (df_usuarios['SENHA'] == senha.strip()) &
                               (df_usuarios['ATIVO'] == 'S')]

        if not usuario.empty:
            # Retorna os dados do usuário como um dicionário
            return usuario.iloc[0].to_dict()
        else:
            print("[ERRO] Usuário ou senha incorretos ou usuário inativo.")
            return None
    except Exception as e:
        print(f"[ERRO] Falha na autenticação: {e}")
        return None
