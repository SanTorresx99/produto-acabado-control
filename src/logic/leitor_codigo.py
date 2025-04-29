# src/logic/leitor_codigo.py

import pandas as pd
import os
from datetime import datetime

# Caminho do arquivo CSV onde os registros das OPs são salvos
REGISTROS_CSV_PATH = os.path.join(os.path.dirname(__file__), '..', 'files', 'registros.csv')

def verificar_codigo_pertencente_op(codigo_barras, cod_op):
    """
    Verifica se o código de barras pertence à OP selecionada no banco ERP.
    Retorna True se o código de barras pertencer à OP, e False caso contrário.
    """
    try:
        # Simulação de consulta ao banco de dados (substituir com a lógica real)
        # Aqui estamos assumindo que o código de barras da OP é validado diretamente.
        # No ambiente real, deverá ser feita uma consulta ao banco ERP para validar se o código de barras pertence à OP

        # Para simplificar, estamos assumindo que o código de barras pertence à OP se não estiver registrado previamente no arquivo de registros
        registros_df = pd.read_csv(REGISTROS_CSV_PATH)
        op_registrada = registros_df[registros_df['COD_OP'] == cod_op]
        if not op_registrada.empty:
            print(f"[OK] O código de barras {codigo_barras} pertence à OP {cod_op}.")
            return True
        else:
            print(f"[ERRO] O código de barras {codigo_barras} não pertence à OP {cod_op}.")
            return False

    except Exception as e:
        print(f"[ERRO] Falha ao verificar código de barras: {e}")
        return False


def registrar_leitura(codigo_barras, cod_op, qtd_prevista):
    """
    Registra a leitura do código de barras no arquivo CSV de registros.
    Realiza as verificações se o código pertence à OP e a quantidade já registrada.

    Parâmetros:
        codigo_barras (str): Código de barras do produto.
        cod_op (str): Código da ordem de produção (OP).
        qtd_prevista (float): Quantidade prevista para a OP.
    """
    try:
        # Passo 1: Verifica se o código de barras pertence à OP
        if not verificar_codigo_pertencente_op(codigo_barras, cod_op):
            return False

        # Passo 2: Verificar quantos registros já foram realizados dessa OP
        registros_df = pd.read_csv(REGISTROS_CSV_PATH)
        
        # Verificar a quantidade registrada para essa OP
        op_registrada = registros_df[registros_df['COD_OP'] == cod_op]
        if op_registrada.empty:
            # Se a OP não estiver registrada, criar a entrada
            print(f"[INFO] OP {cod_op} não registrada, criando nova entrada.")
            registrar_op(cod_op)
            op_registrada = registros_df[registros_df['COD_OP'] == cod_op]  # Recarregar após o registro da OP

        qtd_registrada = op_registrada['QTD_REGISTRADA'].iloc[0]
        print(f"[INFO] Quantidade registrada para OP {cod_op}: {qtd_registrada}/{qtd_prevista}")

        # Passo 3: Verifica se a quantidade registrada é menor que a prevista
        if qtd_registrada >= qtd_prevista:
            resposta = input(f"[ALERTA] A quantidade prevista ({qtd_prevista}) já foi atingida. Deseja continuar registrando (S/N)? ")
            if resposta.lower() != 's':
                print("[INFO] Parando a conferência.")
                return False

        # Passo 4: Atualizar a quantidade registrada para a OP
        registros_df.loc[registros_df['COD_OP'] == cod_op, 'QTD_REGISTRADA'] += 1
        registros_df.to_csv(REGISTROS_CSV_PATH, index=False)

        print(f"[OK] Leitura registrada: Código de barras {codigo_barras} | OP {cod_op} | Total registrado: {qtd_registrada + 1}")
        return True

    except Exception as e:
        print(f"[ERRO] Falha ao registrar leitura: {e}")
        return False


def registrar_op(cod_op):
    """
    Registra uma nova OP no arquivo CSV 'registros.csv' quando a OP ainda não está registrada.

    Parâmetros:
        cod_op (str): Código da OP.
    """
    try:
        # Carregar registros existentes
        if os.path.exists(REGISTROS_CSV_PATH):
            registros_df = pd.read_csv(REGISTROS_CSV_PATH)
        else:
            registros_df = pd.DataFrame(columns=['COD_OP', 'NOME_PRODUTO', 'QTD_REGISTRADA', 'ESPECIE', 'SUB_ESPECIE', 'ID_PRODUTO', 'COD_BARRAS', 'DATA_REGISTRO'])

        # Adicionar a OP como não registrada inicialmente
        nova_op = {
            'COD_OP': cod_op,
            'NOME_PRODUTO': 'Produto Não Identificado',
            'QTD_REGISTRADA': 0,
            'ESPECIE': 'Não Especificado',
            'SUB_ESPECIE': 'Não Especificado',
            'ID_PRODUTO': 0,
            'COD_BARRAS': '',
            'DATA_REGISTRO': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        # Adicionar a nova OP
        registros_df = registros_df.append(nova_op, ignore_index=True)

        # Salvar no arquivo CSV
        registros_df.to_csv(REGISTROS_CSV_PATH, index=False)
        print(f"[OK] OP {cod_op} registrada com sucesso no arquivo de registros.")
        return True

    except Exception as e:
        print(f"[ERRO] Falha ao registrar OP: {e}")
        return False
