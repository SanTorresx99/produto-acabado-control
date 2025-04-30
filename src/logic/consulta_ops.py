# src/logic/consulta_ops.py

from database.conexao import conectar
import pandas as pd

def carregar_ops(data_inicio: str) -> pd.DataFrame:
    """
    Carrega as ordens de produção (OPs) com base na data exata da OP (data_prev_inicio).
    Primeiramente, carrega todas as OPs e depois aplica os filtros de espécie e subespécie.

    Parâmetros:
        data_inicio (str): Data da OP no formato 'YYYY-MM-DD'

    Retorna:
        pd.DataFrame: Tabela com as OPs programadas para a data informada
    """
    conn = conectar()  # A função conectar() já deve usar o banco de dados correto (MENTOR.FDB)
    if not conn:
        return pd.DataFrame()

    sql = f"""
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
            sopp.codigo_barras AS cod_op
        FROM os_producao_linha_prod opp
        LEFT JOIN grade_cor gc ON gc.id_grade_cor = opp.id_grade_cor
        LEFT JOIN produto_grade pg ON pg.id_produto_grade = gc.id_produto_grade
        LEFT JOIN produto p ON p.id_produto = pg.id_produto
        LEFT JOIN codigo_barras cb ON cb.id_produto = p.id_produto
        LEFT JOIN subdivisao_os_prod_linha_prod sopp ON sopp.id_ordem_serv_prod_linha = opp.id_os_producao_linha_prod
        LEFT JOIN periodo_producao pp ON pp.id_periodo_producao = opp.id_periodo_producao
        LEFT JOIN especie e ON e.id_especie = p.id_especie
        LEFT JOIN sub_especie se ON se.id_sub_especie = p.id_sub_especie
        WHERE CAST(opp.data_prev_inicio AS DATE) like '{data_inicio}%'
        ORDER BY opp.id_os_producao_linha_prod DESC
    """

    try:
        # Lê os dados e retorna em formato DataFrame
        df = pd.read_sql(sql, conn)
        print(f"[OK] {len(df)} OPs carregadas de {data_inicio}")
        print(f"Colunas carregadas: {df.columns}")  # Adicionando para verificar as colunas
        return df
    except Exception as e:
        print("[ERRO] Falha na leitura das OPs:", e)
        return pd.DataFrame()
    finally:
        conn.close()

def filtrar_ops_por_esp_especie(df: pd.DataFrame, especie_escolhida: str, subesp_escolhida: str) -> pd.DataFrame:
    """
    Aplica o filtro por espécie e subespécie na tabela de OPs carregada.

    Parâmetros:
        df (pd.DataFrame): DataFrame contendo as OPs carregadas.
        especie_escolhida (str): A espécie selecionada.
        subesp_escolhida (str): A subespécie selecionada.

    Retorna:
        pd.DataFrame: DataFrame com as OPs filtradas por espécie e subespécie.
    """
    if especie_escolhida != 0:
        df = df[df['ESPECIE'] == especie_escolhida]
    if subesp_escolhida != 0:
        df = df[df['SUB_ESPECIE'] == subesp_escolhida]

    return df
