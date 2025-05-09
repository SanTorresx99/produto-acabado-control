import os
import pandas as pd
from datetime import datetime

# Caminho do CSV de registros
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REGISTROS_CSV_PATH = os.path.join(BASE_DIR, "..", "files", "registros.csv")

# Cache interno de códigos válidos por OP (para evitar reprocessar a cada leitura)
CODIGOS_VALIDOS_CACHE = {}

def carregar_csv() -> pd.DataFrame:
    if os.path.exists(REGISTROS_CSV_PATH):
        df = pd.read_csv(REGISTROS_CSV_PATH, sep=",", dtype={"COD_OP": str, "COD_BARRAS": str})
        return df
    else:
        return pd.DataFrame(columns=["COD_OP", "NOME_PRODUTO", "ESPECIE", "SUB_ESPECIE", "ID_PRODUTO",
                                     "COD_BARRAS", "DATA_REGISTRO", "QTD"])

def salvar_csv(df: pd.DataFrame):
    df.to_csv(REGISTROS_CSV_PATH, index=False)

def contar_registradas_op(codigo_op: str) -> int:
    df = carregar_csv()
    return df[df["COD_OP"] == str(codigo_op)].shape[0]

def buscar_dados_op(codigo_op, df_ops=None):
    """Retorna as informações da OP e registros associados"""

    # Se não foi passado um DataFrame, carrega tudo
    if df_ops is None:
        from .consulta_ops import carregar_ops_intervalo
        df_ops = carregar_ops_intervalo("2020-01-01", "2030-12-31")

    df_ops["CODIGO_OP"] = df_ops["CODIGO_OP"].astype(str)
    op_dados = df_ops[df_ops["CODIGO_OP"] == str(codigo_op)]

    if op_dados.empty:
        return {}

    op_info = op_dados.iloc[0].to_dict()

    return {
        "nome_produto": op_info.get("NOME_PRODUTO"),
        "qtd_prevista": int(op_info.get("QTD_PREVISTA", 0)),
        "qtd_registrada": int(op_info.get("QTD_REGISTRADA", 0)),
        "codigo_barras": op_info.get("CODIGO_BARRAS")
    }

def registrar_leitura(codigo_op: str, codigo_barras: str):
    codigo_op = str(codigo_op).strip()
    codigo_barras = str(codigo_barras).strip()

    # Garante que a lista de códigos válidos esteja em cache
    if codigo_op not in CODIGOS_VALIDOS_CACHE:
        buscar_dados_op(codigo_op)

    codigos_validos = CODIGOS_VALIDOS_CACHE.get(codigo_op, [])
    if codigo_barras not in codigos_validos:
        raise ValueError("Código de barras inválido para esta OP")

    df = carregar_csv()

    # Busca os dados da OP no próprio DataFrame
    df_op = df[df["COD_OP"] == codigo_op]
    if df_op.empty:
        raise ValueError("Dados da OP não encontrados no CSV")

    dados_op = df_op.iloc[0]

    novo_registro = {
        "COD_OP": codigo_op,
        "NOME_PRODUTO": dados_op["NOME_PRODUTO"],
        "ESPECIE": dados_op["ESPECIE"],
        "SUB_ESPECIE": dados_op["SUB_ESPECIE"],
        "ID_PRODUTO": dados_op["ID_PRODUTO"],
        "COD_BARRAS": codigo_barras,
        "DATA_REGISTRO": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "QTD": 1
    }

    df = pd.concat([df, pd.DataFrame([novo_registro])], ignore_index=True)
    salvar_csv(df)
