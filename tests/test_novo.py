# src/database/criar_tabelas.py

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.database.conexao import conectar_novo_banco

def criar_tabelas():
    """
    Cria todas as tabelas necessárias no banco de dados de controle de produtos acabados.
    Só executa a criação se as tabelas não existirem.
    """
    conn = conectar_novo_banco()
    if not conn:
        print("[ERRO] Não foi possível conectar ao banco de dados para criar tabelas.")
        return False

    try:
        cursor = conn.cursor()

        # Tabela de Usuários
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS USUARIOS (
                ID_USUARIO INTEGER NOT NULL PRIMARY KEY,
                NOME VARCHAR(100) NOT NULL,
                LOGIN VARCHAR(50) NOT NULL UNIQUE,
                SENHA VARCHAR(255) NOT NULL,
                EMAIL VARCHAR(100),
                NIVEL_ACESSO VARCHAR(20) NOT NULL,
                DATA_CADASTRO TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ATIVO CHAR(1) DEFAULT 'S'
            )
        """)
        
        # Sequência para ID do usuário
        cursor.execute("""
            CREATE SEQUENCE IF NOT EXISTS SEQ_USUARIOS
        """)
        
        # Tabela de Leitura de Produtos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS LEITURA_PRODUTO (
                ID_LEITURA INTEGER NOT NULL PRIMARY KEY,
                CODIGO_BARRAS VARCHAR(50) NOT NULL,
                COD_OP VARCHAR(20) NOT NULL,
                QUANTIDADE DECIMAL(10,2) DEFAULT 1,
                STATUS VARCHAR(20) DEFAULT 'Registrado',
                DATA_REGISTRO TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ID_USUARIO INTEGER,
                OBSERVACAO VARCHAR(255),
                FOREIGN KEY (ID_USUARIO) REFERENCES USUARIOS(ID_USUARIO)
            )
        """)
        
        # Sequência para ID da leitura
        cursor.execute("""
            CREATE SEQUENCE IF NOT EXISTS SEQ_LEITURA_PRODUTO
        """)
        
        # Tabela de Log de Atividades
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS LOGS (
                ID_LOG INTEGER NOT NULL PRIMARY KEY,
                ID_USUARIO INTEGER,
                ACAO VARCHAR(50) NOT NULL,
                TABELA_AFETADA VARCHAR(50),
                DESCRICAO VARCHAR(255),
                DATA_HORA TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                IP_ORIGEM VARCHAR(50),
                FOREIGN KEY (ID_USUARIO) REFERENCES USUARIOS(ID_USUARIO)
            )
        """)
        
        # Sequência para ID do log
        cursor.execute("""
            CREATE SEQUENCE IF NOT EXISTS SEQ_LOGS
        """)
        
        # Tabela de Configurações do Sistema
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS CONFIGURACOES (
                ID_CONFIG INTEGER NOT NULL PRIMARY KEY,
                CHAVE VARCHAR(50) NOT NULL UNIQUE,
                VALOR VARCHAR(255),
                DESCRICAO VARCHAR(255),
                DATA_MODIFICACAO TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Sequência para ID de configuração
        cursor.execute("""
            CREATE SEQUENCE IF NOT EXISTS SEQ_CONFIGURACOES
        """)
        
        # Criar um usuário admin padrão se não existir nenhum usuário
        cursor.execute("SELECT COUNT(*) FROM USUARIOS")
        if cursor.fetchone()[0] == 0:
            # Hash simples para senha 'admin' - em produção usar bcrypt ou similar
            cursor.execute("""
                INSERT INTO USUARIOS (ID_USUARIO, NOME, LOGIN, SENHA, EMAIL, NIVEL_ACESSO)
                VALUES (NEXT VALUE FOR SEQ_USUARIOS, 'Administrador', 'admin', 'admin', 'admin@empresa.com', 'ADMIN')
            """)
            print("[INFO] Usuário administrador padrão criado.")
        
        # Inserir configurações padrão
        cursor.execute("SELECT COUNT(*) FROM CONFIGURACOES")
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                INSERT INTO CONFIGURACOES (ID_CONFIG, CHAVE, VALOR, DESCRICAO)
                VALUES 
                (NEXT VALUE FOR SEQ_CONFIGURACOES, 'VERSAO_SISTEMA', '1.0.0', 'Versão atual do sistema'),
                (NEXT VALUE FOR SEQ_CONFIGURACOES, 'MAX_TENTATIVAS_LOGIN', '5', 'Número máximo de tentativas de login'),
                (NEXT VALUE FOR SEQ_CONFIGURACOES, 'DIAS_EXPIRAR_SENHA', '90', 'Dias para expirar a senha')
            """)
            print("[INFO] Configurações padrão inseridas.")
        
        conn.commit()
        print("[OK] Todas as tabelas e sequências foram criadas com sucesso!")
        return True
        
    except Exception as e:
        conn.rollback()
        print(f"[ERRO] Falha ao criar tabelas: {e}")
        return False
    finally:
        conn.close()

def verificar_estrutura():
    """
    Verifica se todas as tabelas e sequências foram criadas corretamente.
    """
    conn = conectar_novo_banco()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        tabelas = ['USUARIOS', 'LEITURA_PRODUTO', 'LOGS', 'CONFIGURACOES']
        sequencias = ['SEQ_USUARIOS', 'SEQ_LEITURA_PRODUTO', 'SEQ_LOGS', 'SEQ_CONFIGURACOES']
        
        todas_tabelas_ok = True
        print("\n=== VERIFICAÇÃO DE ESTRUTURA DO BANCO DE DADOS ===")
        
        # Verificar tabelas
        print("\nTabelas:")
        for tabela in tabelas:
            try:
                cursor.execute(f"SELECT 1 FROM {tabela} WHERE 1=0")
                print(f"[OK] Tabela {tabela} existe.")
            except Exception:
                todas_tabelas_ok = False
                print(f"[FALHA] Tabela {tabela} não existe ou tem problemas.")
        
        # Verificar sequências
        print("\nSequências:")
        for seq in sequencias:
            try:
                cursor.execute(f"SELECT NEXT VALUE FOR {seq} FROM RDB$DATABASE")
                cursor.fetchone()
                print(f"[OK] Sequência {seq} existe.")
            except Exception:
                todas_tabelas_ok = False
                print(f"[FALHA] Sequência {seq} não existe ou tem problemas.")
        
        return todas_tabelas_ok
    except Exception as e:
        print(f"[ERRO] Erro ao verificar estrutura: {e}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    print("=== CRIAÇÃO E VERIFICAÇÃO DE TABELAS DO BANCO DE DADOS ===")
    if criar_tabelas():
        verificar_estrutura()
    else:
        print("[ERRO] A criação de tabelas falhou. Verifique a conexão com o banco.")