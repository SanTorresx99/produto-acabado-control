# src/logic/consulta_ops.py

import pandas as pd
import os
from datetime import datetime

# Caminho do arquivo CSV onde os registros das OPs são salvos
REGISTROS_CSV_PATH = os.path.join(os.path.dirname(__file__), '..', 'files', 'registros.csv')

def carregar_ops(data_inicio: str) -> pd.DataFrame:
    """
    Carrega as ordens de produção (OPs) com base na data exata da OP (data_prev_inicio).

    Parâmetros:
        data_inicio (str): Data da OP no formato 'YYYY-MM-DD'

    Retorna:
        pd.DataFrame: Tabela com as OPs programadas para a data informada
    """
    try:
        # Simulação de carregamento de dados das OPs do ERP (seria substituída por uma consulta real ao banco de dados MENTOR)
        # Aqui estamos simulando os dados das OPs. Em um ambiente real, deve-se carregar os dados do ERP.

        # Exemplo de dados (substituir com consulta real ao banco)
        ops_data = {
            'ID_PERIOD': [1, 2, 3],
            'ID_OS': [101, 102, 103],
            'CODIGO_OP': ['168343', '168344', '168345'],
            'DATA_PREVISTA': ['2025-04-03', '2025-04-04', '2025-04-05'],
            'ESPECIE': ['ESTOFADOS', 'CAMAS', 'COLCHAO MOLA'],
            'SUB_ESPECIE': ['ESTOFADO 3 LUGARES', 'CAMA SIMPLES', 'COLCHÃO MOLA'],
            'ID_PRODUTO': [1, 2, 3],
            'NOME_PRODUTO': ['Estofado Modelo A', 'Cama Modelo B', 'Colchão Mola C'],
            'QTD_PREVISTA': [500, 300, 200],
            'CODIGO_BARRAS': ['7899600724613', '7899600758571', '7899600771234'],
            'COD_OP': ['168343', '168344', '168345']
        }

        ops_df = pd.DataFrame(ops_data)

        # Filtrando os dados conforme a data informada
        ops_df['DATA_PREVISTA'] = pd.to_datetime(ops_df['DATA_PREVISTA'])
        ops_df = ops_df[ops_df['DATA_PREVISTA'] == pd.to_datetime(data_inicio)]

        print(f"[OK] {len(ops_df)} OPs carregadas de {data_inicio}")
        return ops_df

    except Exception as e:
        print(f"[ERRO] Falha ao carregar OPs: {e}")
        return pd.DataFrame()


def registrar_op(cod_op: str, nome_produto: str, qtd_prevista: float, especie: str, sub_especie: str, id_produto: int, cod_barras: str):
    """
    Registra uma nova OP no arquivo CSV 'registros.csv'.

    Parâmetros:
        cod_op (str): Código da OP.
        nome_produto (str): Nome do produto da OP.
        qtd_prevista (float): Quantidade prevista para a OP.
        especie (str): Espécie do produto.
        sub_especie (str): Subespécie do produto.
        id_produto (int): ID do produto.
        cod_barras (str): Código de barras do produto.
    """
    try:
        # Verificar se o arquivo de registros já existe, caso contrário, criar com cabeçalhos
        if os.path.exists(REGISTROS_CSV_PATH):
            registros_df = pd.read_csv(REGISTROS_CSV_PATH)
        else:
            registros_df = pd.DataFrame(columns=['COD_OP', 'NOME_PRODUTO', 'QTD_REGISTRADA', 'ESPECIE', 'SUB_ESPECIE', 'ID_PRODUTO', 'COD_BARRAS', 'DATA_REGISTRO'])

        # Verificar se a OP já foi registrada
        if cod_op in registros_df['COD_OP'].values:
            print(f"[INFO] OP {cod_op} já registrada anteriormente.")
            return False

        # Adicionar uma nova linha ao DataFrame de registros
        nova_op = {
            'COD_OP': cod_op,
            'NOME_PRODUTO': nome_produto,
            'QTD_REGISTRADA': 0,  # Inicialmente nenhuma quantidade registrada
            'ESPECIE': especie,
            'SUB_ESPECIE': sub_especie,
            'ID_PRODUTO': id_produto,
            'COD_BARRAS': cod_barras,
            'DATA_REGISTRO': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        registros_df = registros_df.append(nova_op, ignore_index=True)

        # Salvar os registros no arquivo CSV
        registros_df.to_csv(REGISTROS_CSV_PATH, index=False)
        print(f"[OK] OP {cod_op} registrada com sucesso no arquivo de registros.")
        return True

    except Exception as e:
        print(f"[ERRO] Falha ao registrar OP: {e}")
        return False