#src/logic/consulta_ops.py
from dotenv import load_dotenv
load_dotenv()

from src.database.conexao import conectar
import pandas as pd
import os

REGISTROS_CSV_PATH = os.path.join(os.path.dirname(__file__), "..","files", "registros.csv")

def carregar_ops_intervalo(data_inicio: str, data_fim: str, codigos_op: list[str] = None, tipo_op: str = "ambos") -> pd.DataFrame:
    conn = conectar()
    if not conn:
        return pd.DataFrame()

    filtro_op = ""
    if codigos_op:
        lista_codigos = ",".join(f"'{cod.strip()}'" for cod in codigos_op if cod.strip())
        filtro_op = f"AND opp.codigo IN ({lista_codigos})"

    queries = []

    if tipo_op in ("linha", "ambos"):
        queries.append(f"""
            SELECT
                pp.id_periodo_producao AS id_period,
                opp.id_os_producao_linha_prod AS id_os,
                opp.codigo AS codigo_op,
                opp.data_prev_inicio AS data_prevista,
                REPLACE(e.nome, 'PRODUTO ACABADO -', '') AS especie,
                se.nome AS sub_especie,
                p.id_produto,
                p.nome AS nome_produto,
                opp.quantidade_ref_prev_prod AS qtd_prevista,
                cb.codigo_barras,
                sopp.codigo_barras AS cod_op,
                'LIN_PROD' AS tipo_op
            FROM os_producao_linha_prod opp
            LEFT JOIN grade_cor gc ON gc.id_grade_cor = opp.id_grade_cor
            LEFT JOIN produto_grade pg ON pg.id_produto_grade = gc.id_produto_grade
            LEFT JOIN produto p ON p.id_produto = pg.id_produto
            LEFT JOIN codigo_barras cb ON cb.id_produto = p.id_produto
            LEFT JOIN subdivisao_os_prod_linha_prod sopp ON sopp.id_ordem_serv_prod_linha = opp.id_os_producao_linha_prod
            LEFT JOIN periodo_producao pp ON pp.id_periodo_producao = opp.id_periodo_producao
            LEFT JOIN especie e ON e.id_especie = p.id_especie
            LEFT JOIN sub_especie se ON se.id_sub_especie = p.id_sub_especie
            WHERE CAST(opp.data_prev_inicio AS DATE) BETWEEN '{data_inicio}' AND '{data_fim}'
            {filtro_op}
        """)

    if tipo_op in ("sob_encomenda", "ambos"):
        queries.append(f"""
            SELECT
                pp.id_periodo_producao AS id_period,
                opp.id_os_sob_enc AS id_os,
                opp.codigo AS codigo_op,
                opp.data_prev_inicio AS data_prevista,
                REPLACE(e.nome, 'PRODUTO ACABADO -', '') AS especie,
                se.nome AS sub_especie,
                p.id_produto,
                p.nome AS nome_produto,
                opp.quantidade_prev_prod AS qtd_prevista,
                cb.codigo_barras,
                sopp.codigo_barras AS cod_op,
                'SOB_ENC' AS tipo_op
            FROM os_producao_sob_enc opp
            LEFT JOIN grade_cor gc ON gc.id_grade_cor = opp.id_grade_cor
            LEFT JOIN produto_grade pg ON pg.id_produto_grade = gc.id_produto_grade
            LEFT JOIN produto p ON p.id_produto = pg.id_produto
            LEFT JOIN codigo_barras cb ON cb.id_produto = p.id_produto
            LEFT JOIN subdivisao_os_prod_sob_enc sopp ON sopp.id_os_prod_sob_enc = opp.id_os_sob_enc
            LEFT JOIN periodo_producao pp ON pp.id_periodo_producao = opp.id_periodo_producao
            LEFT JOIN especie e ON e.id_especie = p.id_especie
            LEFT JOIN sub_especie se ON se.id_sub_especie = p.id_sub_especie
            WHERE CAST(opp.data_prev_inicio AS DATE) BETWEEN '{data_inicio}' AND '{data_fim}'
            {filtro_op}
        """)

    try:
        dfs = [pd.read_sql(q, conn) for q in queries]
        df_final = pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()

        # Enriquecimento com registros.csv
        if os.path.exists(REGISTROS_CSV_PATH):
            registros = pd.read_csv(REGISTROS_CSV_PATH, sep=",")
            registros["COD_OP"] = registros["COD_OP"].astype(str).str.strip()

            # 🔧 Corrige valores ausentes ou inválidos na coluna QTD
            registros["QTD"] = pd.to_numeric(registros["QTD"], errors="coerce").fillna(1).astype(int)

            # Agrupamento após correção
            soma_registrada = registros.groupby("COD_OP")["QTD"].sum().reset_index()
            soma_registrada.columns = ["CODIGO_OP", "QTD_REGISTRADA"]
            soma_registrada["CODIGO_OP"] = soma_registrada["CODIGO_OP"].astype(str)

            df_final["CODIGO_OP"] = df_final["CODIGO_OP"].astype(str)
            df_final = df_final.merge(soma_registrada, on="CODIGO_OP", how="left")

        else:
            df_final["QTD_REGISTRADA"] = 0

        df_final["QTD_REGISTRADA"] = df_final["QTD_REGISTRADA"].fillna(0).astype(int)
        df_final["STATUS"] = df_final["QTD_REGISTRADA"].apply(lambda x: "Registrado" if x > 0 else "")

        print(f"[OK] {len(df_final)} OPs carregadas entre {data_inicio} e {data_fim} (tipo_op: {tipo_op})")
        return df_final

    except Exception as e:
        print("[ERRO] Falha na leitura das OPs:", e)
        return pd.DataFrame()
    finally:
        conn.close()

def filtrar_ops_por_esp_especie(df: pd.DataFrame, especie_escolhida: str, subesp_escolhida: str) -> pd.DataFrame:
    if especie_escolhida and especie_escolhida.lower() != "todas":
        df = df[df['ESPECIE'] == especie_escolhida]
    if subesp_escolhida and subesp_escolhida.lower() != "todas":
        df = df[df['SUB_ESPECIE'] == subesp_escolhida]
    return df

def obter_subespecies(df: pd.DataFrame):
    return sorted(df["SUB_ESPECIE"].dropna().unique())
