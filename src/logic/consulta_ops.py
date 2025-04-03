from database.conexao import conectar
import pandas as pd

def carregar_ops(data_inicio: str, data_fim: str) -> pd.DataFrame:
    conn = conectar()
    if not conn:
        return pd.DataFrame()

    sql = f"""
        select * from produto
    """

    try:
        df = pd.read_sql(sql, conn)
        print(f"[OK] {len(df)} OPs carregadas entre {data_inicio} e {data_fim}")
        return df
    except Exception as e:
        print("[ERRO] Falha na leitura das OPs:", e)
        return pd.DataFrame()
    finally:
        conn.close()
