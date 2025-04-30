import pandas as pd
import os
from datetime import datetime

# Caminho do arquivo CSV onde os registros das OPs são salvos
REGISTROS_CSV_PATH = os.path.join(os.path.dirname(__file__), '..', 'files', 'registros.csv')

def verificar_codigo_pertencente_op(codigo_barras, cod_op, dados_op=None):
    """
    Verifica se o código de barras pertence à OP selecionada.
    """
    try:
        if dados_op and 'CODIGO_BARRAS' in dados_op and dados_op['CODIGO_BARRAS']:
            codigo_barras_correto = str(dados_op['CODIGO_BARRAS'])
            if codigo_barras != codigo_barras_correto:
                print(f"[ERRO] O código de barras {codigo_barras} NÃO pertence à OP {cod_op}.")
                print(f"[INFO] Código de barras correto para esta OP: {codigo_barras_correto}")
                return False

        print(f"[OK] O código de barras {codigo_barras} pertence à OP {cod_op}.")
        return True

    except Exception as e:
        print(f"[ERRO] Falha ao verificar código de barras: {e}")
        return False

def registrar_leitura(codigo_barras, cod_op, dados_op=None):
    """
    Registra uma nova leitura como uma linha no CSV com QTD = 1.
    """
    try:
        # Verifica se o código de barras é válido
        if not verificar_codigo_pertencente_op(codigo_barras, cod_op, dados_op):
            return False

        # Garantir que o diretório existe
        os.makedirs(os.path.dirname(REGISTROS_CSV_PATH), exist_ok=True)

        # Criar estrutura se o arquivo não existir
        if not os.path.exists(REGISTROS_CSV_PATH):
            registros_df = pd.DataFrame(columns=[
                'COD_OP', 'NOME_PRODUTO', 'QTD', 'ESPECIE', 'SUB_ESPECIE',
                'ID_PRODUTO', 'COD_BARRAS', 'DATA_REGISTRO'
            ])
        else:
            registros_df = pd.read_csv(REGISTROS_CSV_PATH)

        # Criar nova linha de registro
        nova_linha = {
            'COD_OP': cod_op,
            'NOME_PRODUTO': dados_op.get('NOME_PRODUTO', 'Produto Não Identificado'),
            'QTD': 1,
            'ESPECIE': dados_op.get('ESPECIE', 'Não Especificado'),
            'SUB_ESPECIE': dados_op.get('SUB_ESPECIE', 'Não Especificado'),
            'ID_PRODUTO': dados_op.get('ID_PRODUTO', 0),
            'COD_BARRAS': str(codigo_barras),
            'DATA_REGISTRO': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        # Adicionar nova linha
        registros_df = pd.concat([registros_df, pd.DataFrame([nova_linha])], ignore_index=True)

        # Salvar
        registros_df.to_csv(REGISTROS_CSV_PATH, index=False)
        print(f"[OK] Leitura registrada: OP {cod_op} | Código: {codigo_barras} | QTD: 1")
        return True

    except Exception as e:
        print(f"[ERRO] Falha ao registrar leitura: {e}")
        return False
