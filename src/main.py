import sys
import os
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))
from logic.consulta_ops import carregar_ops, filtrar_ops_por_esp_especie
from logic.leitor_codigo import registrar_leitura, REGISTROS_CSV_PATH
from logic.usuario import autenticar_usuario

def main():
    print("=== SISTEMA DE APONTAMENTO DE PRODUÇÃO ===")

    # Passo 1: Login
    while True:
        login = input("Digite seu login: ")
        senha = input("Digite sua senha: ")

        usuario = autenticar_usuario(login, senha)
        if usuario:
            print(f"[OK] Bem-vindo, {usuario['NOME']}!")
            break
        else:
            print("[ERRO] Usuário ou senha incorretos ou usuário inativo.")

    # Passo 2: Data da OP
    while True:
        data = input("Informe a data da OP (YYYY-MM-DD ou 'sair' para encerrar): ")
        if data.lower() == 'sair':
            print("[INFO] Encerrando sistema.")
            break

        print(f"[INFO] Carregando OPs para a data {data}...")
        ops_disponiveis = carregar_ops(data)
        if ops_disponiveis.empty:
            print("[ERRO] Nenhuma OP encontrada para a data informada.")
            continue

        print(f"[INFO] {len(ops_disponiveis)} OPs carregadas de {data}")
        print(f"Colunas carregadas: {ops_disponiveis.columns}")

        # Passo 3: Filtro por Espécie
        print("\n=== ESPÉCIES DISPONÍVEIS ===")
        for idx, especie in enumerate(ops_disponiveis['ESPECIE'].unique(), 1):
            print(f"[{idx}] {especie}")

        especie_escolhida = int(input("Selecione uma espécie ou 0 para ignorar: "))
        if especie_escolhida == 0:
            print("[OK] Ignorando espécie.")
            especie_selecionada = 0
        else:
            especie_selecionada = ops_disponiveis['ESPECIE'].unique()[especie_escolhida - 1]
            print(f"[OK] Espécie selecionada: {especie_selecionada}")
            ops_disponiveis = filtrar_ops_por_esp_especie(ops_disponiveis, especie_selecionada, 0)

        # Passo 4: Filtro por Subespécie
        print("\n=== SUBESPÉCIES DISPONÍVEIS ===")
        for idx, subesp in enumerate(ops_disponiveis['SUB_ESPECIE'].unique(), 1):
            print(f"[{idx}] {subesp}")

        subesp_escolhida = int(input("Selecione uma subespécie ou 0 para ignorar: "))
        if subesp_escolhida == 0:
            print("[OK] Ignorando subespécie.")
            subesp_selecionada = 0
        else:
            subesp_selecionada = ops_disponiveis['SUB_ESPECIE'].unique()[subesp_escolhida - 1]
            print(f"[OK] Subespécie selecionada: {subesp_selecionada}")
            ops_disponiveis = filtrar_ops_por_esp_especie(ops_disponiveis, especie_selecionada, subesp_selecionada)

        # Passo 5: Escolher OP
        print("\n=== OPs disponíveis ===")
        for idx, op in enumerate(ops_disponiveis['CODIGO_OP'].unique(), 1):
            produto = ops_disponiveis[ops_disponiveis['CODIGO_OP'] == op]['NOME_PRODUTO'].iloc[0]
            qtd = ops_disponiveis[ops_disponiveis['CODIGO_OP'] == op]['QTD_PREVISTA'].iloc[0]
            print(f"[{idx}] OP: {op} | Produto: {produto} | Qtde: {qtd}")

        while True:
            try:
                op_escolhida = int(input("Digite o número da OP para iniciar conferência: "))
                if 1 <= op_escolhida <= len(ops_disponiveis['CODIGO_OP'].unique()):
                    break
                else:
                    print("[ERRO] Número fora do intervalo.")
            except ValueError:
                print("[ERRO] Digite um número válido.")

        idx_op = op_escolhida - 1
        codigo_op = ops_disponiveis['CODIGO_OP'].unique()[idx_op]
        op_selecionada = ops_disponiveis[ops_disponiveis['CODIGO_OP'] == codigo_op].iloc[0]
        cod_op = op_selecionada['CODIGO_OP']
        produto = op_selecionada['NOME_PRODUTO']
        qtd_prevista = op_selecionada['QTD_PREVISTA']
        dados_op = op_selecionada.to_dict()

        print(f"[OK] OP selecionada: {cod_op} | Produto: {produto} | Qtde: {qtd_prevista}")

        # Passo 6: Leitura do código de barras

        # Contar registros anteriores da OP + Produto
        total_lidos = 0
        if os.path.exists(REGISTROS_CSV_PATH):
            try:
                registros_df = pd.read_csv(REGISTROS_CSV_PATH)
                registros_filtrados = registros_df[
                    (registros_df['COD_OP'] == cod_op) &
                    (registros_df['ID_PRODUTO'] == dados_op['ID_PRODUTO'])
                ]
                total_lidos = len(registros_filtrados)
            except Exception as e:
                print(f"[ERRO] Falha ao ler registros anteriores: {e}")

        print(f"\n=== INÍCIO DA CONFERÊNCIA ===")
        print(f"[INFO] Produto: {produto}")
        print(f"[INFO] OP: {cod_op}")
        print(f"[INFO] Quantidade prevista: {qtd_prevista}")
        print(f"[INFO] Quantidade já registrada: {total_lidos}\n")

        while True:
            codigo_barras = input("Digite ou escaneie o código de barras do produto (ou 'sair' para encerrar): ")
            if codigo_barras.lower() == "sair":
                print("[INFO] Encerrando conferência.")
                break

            if registrar_leitura(codigo_barras, cod_op, dados_op):
                total_lidos += 1
                print(f"[INFO] Leitura registrada com sucesso. Total lido: {total_lidos}")
            else:
                print("[ERRO] Código de barras inválido ou já registrado.")

if __name__ == "__main__":
    main()
