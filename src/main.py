import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))
from logic.consulta_ops import carregar_ops, filtrar_ops_por_esp_especie
from logic.leitor_codigo import registrar_leitura
from logic.usuario import autenticar_usuario
import pandas as pd

def main():
    print("=== SISTEMA DE APONTAMENTO DE PRODUÇÃO ===")

    # Passo 1: Realiza o login
    while True:
        login = input("Digite seu login: ")
        senha = input("Digite sua senha: ")

        usuario = autenticar_usuario(login, senha)
        if usuario:
            print(f"[OK] Bem-vindo, {usuario['NOME']}!")
            break
        else:
            print("[ERRO] Usuário ou senha incorretos ou usuário inativo.")

    # Passo 2: Solicitar a data da OP
    while True:
        data = input("Informe a data da OP (YYYY-MM-DD ou 'sair' para encerrar): ")
        if data.lower() == 'sair':
            print("[INFO] Encerrando sistema.")
            break

        print(f"[INFO] Carregando OPs para a data {data}...")

        # Carregar OPs da data selecionada
        ops_disponiveis = carregar_ops(data)
        if ops_disponiveis.empty:
            print("[ERRO] Nenhuma OP encontrada para a data informada.")
            continue

        print(f"[INFO] {len(ops_disponiveis)} OPs carregadas de {data}")
        print(f"Colunas carregadas: {ops_disponiveis.columns}")

        # Passo 3: Filtragem por Espécie (caso seja necessário)
        print("\n=== ESPÉCIE DISPONÍVEIS ===")
        for idx, especie in enumerate(ops_disponiveis['ESPECIE'].unique(), 1):
            print(f"[{idx}] {especie}")

        especie_escolhida = int(input(f"Selecione uma espécie ou 0 para ignorar: "))
        if especie_escolhida == 0:
            print("[OK] Ignorando espécie.")
            especie_selecionada = 0
        else:
            especie_selecionada = ops_disponiveis['ESPECIE'].unique()[especie_escolhida - 1]
            print(f"[OK] Espécie selecionada: {especie_selecionada}")
            ops_disponiveis = filtrar_ops_por_esp_especie(ops_disponiveis, especie_selecionada, 0)

        # Passo 4: Filtragem por Subespécie (caso seja necessário)
        print("\n=== SUBESPÉCIE DISPONÍVEIS ===")
        for idx, subesp in enumerate(ops_disponiveis['SUB_ESPECIE'].unique(), 1):
            print(f"[{idx}] {subesp}")

        subesp_escolhida = int(input(f"Selecione uma subespécie ou 0 para ignorar: "))
        if subesp_escolhida == 0:
            print("[OK] Ignorando subespécie.")
            subesp_selecionada = 0
        else:
            subesp_selecionada = ops_disponiveis['SUB_ESPECIE'].unique()[subesp_escolhida - 1]
            print(f"[OK] Subespécie selecionada: {subesp_selecionada}")
            ops_disponiveis = filtrar_ops_por_esp_especie(ops_disponiveis, especie_selecionada, subesp_selecionada)

        # Passo 5: Seleção da OP para conferência (sem opção de pular)
        print("\n=== OPs disponíveis ===")
        for idx, op in enumerate(ops_disponiveis['CODIGO_OP'].unique(), 1):
            produto = ops_disponiveis[ops_disponiveis['CODIGO_OP'] == op]['NOME_PRODUTO'].iloc[0]
            qtd = ops_disponiveis[ops_disponiveis['CODIGO_OP'] == op]['QTD_PREVISTA'].iloc[0]
            print(f"[{idx}] OP: {op} | Produto: {produto} | Qtde: {qtd}")

        # Validar a seleção da OP (sem opção de pular)
        while True:
            try:
                op_escolhida = int(input(f"Digite o número da OP para iniciar conferência: "))
                if 1 <= op_escolhida <= len(ops_disponiveis['CODIGO_OP'].unique()):
                    break
                else:
                    print(f"[ERRO] Selecione um número de OP válido entre 1 e {len(ops_disponiveis['CODIGO_OP'].unique())}.")
            except ValueError:
                print("[ERRO] Digite um número válido.")

        # Obter os dados da OP selecionada
        idx_op = op_escolhida - 1
        codigo_op = ops_disponiveis['CODIGO_OP'].unique()[idx_op]
        op_selecionada = ops_disponiveis[ops_disponiveis['CODIGO_OP'] == codigo_op].iloc[0]
        cod_op = op_selecionada['CODIGO_OP']
        produto = op_selecionada['NOME_PRODUTO']
        qtd_prevista = op_selecionada['QTD_PREVISTA']

        # Extrair todos os dados da OP selecionada para passar ao registrar_leitura
        dados_op = op_selecionada.to_dict()

        print(f"[OK] OP selecionada: {cod_op} | Produto: {produto} | Qtde: {qtd_prevista}")

        # Passo 6: Leitura do código de barras
        qtd_registrada = 0
        while qtd_registrada < qtd_prevista:
            codigo_barras = input(f"Digite ou escaneie o código de barras do produto (ou 'sair' para encerrar): ")
            if codigo_barras.lower() == "sair":
                print("[INFO] Encerrando conferência.")
                break

            # Verificar se o código de barras é válido e passa os dados completos da OP
            if registrar_leitura(codigo_barras, cod_op, qtd_prevista, dados_op):
                qtd_registrada += 1
                print(f"[INFO] {qtd_registrada}/{qtd_prevista} registrados.")
            else:
                print("[ERRO] Código de barras inválido ou já registrado.")

            if qtd_registrada >= qtd_prevista:
                print(f"[INFO] Quantidade máxima de {qtd_prevista} já registrada para esta OP.")
                resposta = input("Deseja continuar registrando (S/N)? ")
                if resposta.lower() != 's':
                    break

if __name__ == "__main__":
    main()