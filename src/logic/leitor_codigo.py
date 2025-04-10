# src/logic/leitor_codigo.py

from database.conexao import conectar
from database.conexao import conectar_novo_banco
import pandas as pd

def registrar_leitura(codigo_barras: str, cod_op: str) -> bool:
    """
    Registra a leitura de um código de barras para a OP selecionada e verifica se o código de barras
    já foi registrado.

    Parâmetros:
        codigo_barras (str): Código de barras do produto.
        cod_op (str): Código da ordem de produção (OP).

    Retorna:
        bool: True se a leitura foi registrada com sucesso, False caso contrário.
    """
    conn = conectar_novo_banco()  # Usando a nova conexão com o banco
    if not conn:
        return False

    try:
        # Verificar se o código de barras já foi registrado para a OP selecionada
        sql_verificar = f"""
            SELECT COUNT(*) FROM LEITURA_PRODUTO
            WHERE CODIGO_BARRAS = '{codigo_barras}' AND COD_OP = '{cod_op}'
        """
        df = pd.read_sql(sql_verificar, conn)
        if df.iloc[0, 0] > 0:
            print("[ERRO] Código de barras já registrado para esta OP.")
            return False

        # Registrar o código de barras
        sql_inserir = f"""
            INSERT INTO LEITURA_PRODUTO (CODIGO_BARRAS, COD_OP, QUANTIDADE, STATUS)
            VALUES ('{codigo_barras}', '{cod_op}', 1, 'Registrado')
        """
        conn.execute(sql_inserir)
        conn.commit()
        print(f"[OK] Leitura registrada: Código: {codigo_barras} | OP: {cod_op}")
        return True

    except Exception as e:
        print(f"[ERRO] Falha ao registrar leitura: {e}")
        return False
    finally:
        conn.close()