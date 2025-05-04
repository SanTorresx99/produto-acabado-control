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
        if not dados_op or not dados_op.get('CODIGO_BARRAS'):
            print("[ERRO] Código de barras esperado não informado nos dados da OP.")
            return False

        codigo_barras_correto = str(dados_op['CODIGO_BARRAS']).strip()
        codigo_barras_lido = str(codigo_barras).strip()

        print(f"[DEBUG] Comparando código: lido='{codigo_barras_lido}' | esperado='{codigo_barras_correto}'")

        if not codigo_barras_correto.isdigit() or not codigo_barras_lido.isdigit():
            print("[ERRO] Código de barras inválido: contém caracteres não numéricos.")
            return False

        if len(codigo_barras_lido) != len(codigo_barras_correto):
            print(f"[ERRO] Comprimento incorreto do código: {len(codigo_barras_lido)} (esperado {len(codigo_barras_correto)})")
            return False

        if codigo_barras_lido != codigo_barras_correto:
            print(f"[ERRO] Código incorreto: {codigo_barras_lido} ≠ {codigo_barras_correto}")
            return False

        print(f"[OK] Código válido: {codigo_barras_lido} pertence à OP {cod_op}.")
        return True

    except Exception as e:
        print(f"[ERRO] Falha ao verificar código de barras: {e}")
        return False

def registrar_leitura(codigo_barras, cod_op, dados_op=None):
    """
    Registra uma nova leitura como uma linha no CSV com QTD = 1.
    """
    try:
        if not verificar_codigo_pertencente_op(codigo_barras, cod_op, dados_op):
            print(f"[ERRO] Código de barras não registrado devido a falha na verificação.")
            return False

        os.makedirs(os.path.dirname(REGISTROS_CSV_PATH), exist_ok=True)

        if not os.path.exists(REGISTROS_CSV_PATH):
            registros_df = pd.DataFrame(columns=[
                'COD_OP', 'NOME_PRODUTO', 'QTD', 'ESPECIE', 'SUB_ESPECIE',
                'ID_PRODUTO', 'COD_BARRAS', 'DATA_REGISTRO'
            ])
        else:
            registros_df = pd.read_csv(REGISTROS_CSV_PATH)

        nova_linha = {
            'COD_OP': cod_op,
            'NOME_PRODUTO': dados_op.get('NOME_PRODUTO', 'Produto Não Identificado'),
            'QTD': 1,
            'ESPECIE': dados_op.get('ESPECIE', 'Não Especificado'),
            'SUB_ESPECIE': dados_op.get('SUB_ESPECIE', 'Não Especificado'),
            'ID_PRODUTO': dados_op.get('ID_PRODUTO', 0),
            'COD_BARRAS': str(codigo_barras).strip(),
            'DATA_REGISTRO': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        registros_df = pd.concat([registros_df, pd.DataFrame([nova_linha])], ignore_index=True)

        registros_df.to_csv(REGISTROS_CSV_PATH, index=False)
        print(f"[OK] Leitura registrada: OP {cod_op} | Código: {codigo_barras} | QTD: 1")
        return True

    except Exception as e:
        print(f"[ERRO] Falha ao registrar leitura: {e}")
        return False
