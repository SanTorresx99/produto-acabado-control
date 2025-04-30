import pandas as pd
import os
from datetime import datetime

# Caminho do arquivo CSV onde os registros das OPs são salvos
REGISTROS_CSV_PATH = os.path.join(os.path.dirname(__file__), '..', 'files', 'registros.csv')

def verificar_codigo_pertencente_op(codigo_barras, cod_op, dados_op=None):
    """
    Verifica se o código de barras pertence à OP selecionada no banco ERP.
    Retorna True se o código de barras pertencer à OP, e False caso contrário.

    Parâmetros:
        codigo_barras (str): Código de barras a ser verificado.
        cod_op (str): Código da OP para verificação.
        dados_op (dict, opcional): Dados completos da OP, incluindo o código de barras correto.
    """
    try:
        # Se temos os dados da OP com o código de barras correto, validar
        if dados_op and 'CODIGO_BARRAS' in dados_op and dados_op['CODIGO_BARRAS']:
            codigo_barras_correto = str(dados_op['CODIGO_BARRAS'])
            
            # Verificar se o código de barras digitado corresponde ao da OP
            if codigo_barras != codigo_barras_correto:
                print(f"[ERRO] O código de barras {codigo_barras} NÃO pertence à OP {cod_op}.")
                print(f"[INFO] Código de barras correto para esta OP: {codigo_barras_correto}")
                return False
        
        # Verificar se o arquivo existe antes de tentar lê-lo
        if not os.path.exists(REGISTROS_CSV_PATH):
            # Se for o primeiro registro (arquivo não existe), aceitar o código
            print(f"[INFO] Arquivo de registros não existe. Validação inicial para o código de barras: {codigo_barras}")
            # Se temos dados_op e não validamos acima, é pq não tinha código de barras nos dados
            if not dados_op or 'CODIGO_BARRAS' not in dados_op or not dados_op['CODIGO_BARRAS']:
                print(f"[ALERTA] Código de barras não especificado na OP. Aceitando o código informado.")
                return True
            return True
            
        # Verificar se o arquivo está vazio
        if os.path.getsize(REGISTROS_CSV_PATH) == 0:
            print(f"[INFO] Arquivo de registros está vazio. Validação inicial para o código de barras: {codigo_barras}")
            # Se temos dados_op e não validamos acima, é pq não tinha código de barras nos dados
            if not dados_op or 'CODIGO_BARRAS' not in dados_op or not dados_op['CODIGO_BARRAS']:
                print(f"[ALERTA] Código de barras não especificado na OP. Aceitando o código informado.")
                return True
            return True
            
        # Carregar o arquivo de registros
        registros_df = pd.read_csv(REGISTROS_CSV_PATH)
        
        print(f"[OK] O código de barras {codigo_barras} pertence à OP {cod_op}.")
        return True

    except Exception as e:
        print(f"[ERRO] Falha ao verificar código de barras: {e}")
        print(f"[INFO] Rejeitando o código de barras {codigo_barras} devido a erro de verificação")
        return False


def registrar_leitura(codigo_barras, cod_op, qtd_prevista, dados_op=None):
    """
    Registra a leitura do código de barras no arquivo CSV de registros.
    Realiza as verificações se o código pertence à OP e a quantidade já registrada.

    Parâmetros:
        codigo_barras (str): Código de barras do produto.
        cod_op (str): Código da ordem de produção (OP).
        qtd_prevista (float): Quantidade prevista para a OP.
        dados_op (dict, opcional): Dicionário com os dados completos da OP.
    """
    try:
        # Passo 1: Verifica se o código de barras pertence à OP
        if not verificar_codigo_pertencente_op(codigo_barras, cod_op, dados_op):
            return False

        # Passo 2: Garantir que o diretório existe
        os.makedirs(os.path.dirname(REGISTROS_CSV_PATH), exist_ok=True)
        
        # Passo 3: Verificar se o arquivo existe
        if not os.path.exists(REGISTROS_CSV_PATH) or os.path.getsize(REGISTROS_CSV_PATH) == 0:
            # Criar o arquivo com cabeçalho
            registros_df = pd.DataFrame(columns=['COD_OP', 'NOME_PRODUTO', 'QTD_REGISTRADA', 'ESPECIE', 'SUB_ESPECIE', 'ID_PRODUTO', 'COD_BARRAS', 'DATA_REGISTRO'])
            registros_df.to_csv(REGISTROS_CSV_PATH, index=False)
            print(f"[INFO] Arquivo de registros criado: {REGISTROS_CSV_PATH}")
        
        # Passo 4: Verificar quantos registros já foram realizados dessa OP
        registros_df = pd.read_csv(REGISTROS_CSV_PATH)
        
        # Verificar a quantidade registrada para essa OP
        op_registrada = registros_df[registros_df['COD_OP'] == cod_op]
        if op_registrada.empty:
            # Se a OP não estiver registrada, criar a entrada
            print(f"[INFO] OP {cod_op} não registrada, criando nova entrada.")
            registrar_op(cod_op, dados_op)
            registros_df = pd.read_csv(REGISTROS_CSV_PATH)  # Recarregar após o registro da OP
            op_registrada = registros_df[registros_df['COD_OP'] == cod_op]
        
        if op_registrada.empty:
            print(f"[ERRO] Não foi possível registrar a OP {cod_op}. Verifique o arquivo de registros.")
            return False
            
        qtd_registrada = op_registrada['QTD_REGISTRADA'].iloc[0]
        print(f"[INFO] Quantidade registrada para OP {cod_op}: {qtd_registrada}/{qtd_prevista}")

        # Passo 5: Verifica se a quantidade registrada é menor que a prevista
        if qtd_registrada >= qtd_prevista:
            resposta = input(f"[ALERTA] A quantidade prevista ({qtd_prevista}) já foi atingida. Deseja continuar registrando (S/N)? ")
            if resposta.lower() != 's':
                print("[INFO] Parando a conferência.")
                return False

        # Passo 6: Atualizar a quantidade registrada para a OP
        registros_df.loc[registros_df['COD_OP'] == cod_op, 'QTD_REGISTRADA'] += 1
        
        # Atualizar o código de barras lido (opcional, se quiser manter o histórico do último código lido)
        # Converter para string antes de atribuir para evitar o warning de incompatibilidade de tipo
        registros_df.loc[registros_df['COD_OP'] == cod_op, 'COD_BARRAS'] = str(codigo_barras)
        
        registros_df.to_csv(REGISTROS_CSV_PATH, index=False)

        print(f"[OK] Leitura registrada: Código de barras {codigo_barras} | OP {cod_op} | Total registrado: {qtd_registrada + 1}")
        return True

    except Exception as e:
        print(f"[ERRO] Falha ao registrar leitura: {e}")
        return False


def registrar_op(cod_op, dados_op=None):
    """
    Registra uma nova OP no arquivo CSV 'registros.csv' quando a OP ainda não está registrada.

    Parâmetros:
        cod_op (str): Código da OP.
        dados_op (dict, opcional): Dicionário com os dados completos da OP.
    """
    try:
        # Garantir que o diretório existe
        os.makedirs(os.path.dirname(REGISTROS_CSV_PATH), exist_ok=True)
        
        # Verifica se o arquivo existe. Se não existir, cria um DataFrame com as colunas necessárias
        if os.path.exists(REGISTROS_CSV_PATH) and os.path.getsize(REGISTROS_CSV_PATH) > 0:
            registros_df = pd.read_csv(REGISTROS_CSV_PATH)
        else:
            # Se o arquivo não existir ou estiver vazio, cria o arquivo com a estrutura necessária
            registros_df = pd.DataFrame(columns=['COD_OP', 'NOME_PRODUTO', 'QTD_REGISTRADA', 'ESPECIE', 'SUB_ESPECIE', 'ID_PRODUTO', 'COD_BARRAS', 'DATA_REGISTRO'])

        # Se não recebeu dados_op, usar valores padrão
        if dados_op is None:
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
        else:
            # Usar os dados completos da OP
            nova_op = {
                'COD_OP': cod_op,
                'NOME_PRODUTO': dados_op.get('NOME_PRODUTO', 'Produto Não Identificado'),
                'QTD_REGISTRADA': 0,
                'ESPECIE': dados_op.get('ESPECIE', 'Não Especificado'),
                'SUB_ESPECIE': dados_op.get('SUB_ESPECIE', 'Não Especificado'),
                'ID_PRODUTO': dados_op.get('ID_PRODUTO', 0),
                'COD_BARRAS': str(dados_op.get('CODIGO_BARRAS', '')),  # Converter para string
                'DATA_REGISTRO': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }

        # Adicionar a nova OP usando concat ao invés de append (que está depreciado)
        registros_df = pd.concat([registros_df, pd.DataFrame([nova_op])], ignore_index=True)

        # Salvar no arquivo CSV
        registros_df.to_csv(REGISTROS_CSV_PATH, index=False)
        print(f"[OK] OP {cod_op} registrada com sucesso no arquivo de registros.")
        return True

    except Exception as e:
        print(f"[ERRO] Falha ao registrar OP: {e}")
        return False