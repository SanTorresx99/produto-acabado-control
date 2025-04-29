import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))
from logic.consulta_ops import carregar_ops
from logic.validacoes import validar_qtd
from logic.leitor_codigo import registrar_op  # Nova importação

def main():
    print("=== SISTEMA DE APONTAMENTO DE PRODUÇÃO ===")

    while True:
        # Passo 1: Solicitar a data da OP
        data = input("Informe a data da OP (YYYY-MM-DD ou 'sair' para encerrar): ")
        if data.lower() == "sair":
            print("[INFO] Encerrando sistema.")
            break

        print(f"[INFO] Carregando OPs para a data {data}...")

        # Carregar OPs da data selecionada
        ops_disponiveis = carregar_ops(data)
        if ops_disponiveis.empty:
            print("[ERRO] Nenhuma OP encontrada para a data informada.")
            continue

        # Passo 2: Verificar as colunas carregadas
        print(f"Colunas carregadas: {ops_disponiveis.columns}")  # Adicionando para verificar as colunas

        # Passo 3: Filtragem por Espécie (caso seja necessário)
        print("\n=== ESPÉCIE DISPONÍVEIS ===")
        for idx, especie in enumerate(ops_disponiveis['ESPECIE'].unique(), 1):  # Alterado aqui
            print(f"[{idx}] {especie}")
        especie_escolhida = int(input(f"Selecione uma espécie ou 0 para ignorar: "))
        if especie_escolhida == 0:
            print("[OK] Ignorando espécie.")
        else:
            especie_selecionada = ops_disponiveis['ESPECIE'].unique()[especie_escolhida - 1]  # Alterado aqui
            print(f"[OK] Espécie selecionada: {especie_selecionada}")
            ops_disponiveis = ops_disponiveis[ops_disponiveis['ESPECIE'] == especie_selecionada]  # Alterado aqui
            print(f"[INFO] Número de OPs filtradas para a espécie {especie_selecionada}: {len(ops_disponiveis)}")

        # Passo 4: Filtragem por Subespécie (caso seja necessário)
        print("\n=== SUBESPÉCIE DISPONÍVEIS ===")
        for idx, subesp in enumerate(ops_disponiveis['SUB_ESPECIE'].unique(), 1):  # Alterado aqui
            print(f"[{idx}] {subesp}")
        subesp_escolhida = int(input(f"Selecione uma subespécie ou 0 para ignorar: "))
        if subesp_escolhida == 0:
            print("[OK] Ignorando subespécie.")
        else:
            subesp_selecionada = ops_disponiveis['SUB_ESPECIE'].unique()[subesp_escolhida - 1]  # Alterado aqui
            print(f"[OK] Subespécie selecionada: {subesp_selecionada}")
            ops_disponiveis = ops_disponiveis[ops_disponiveis['SUB_ESPECIE'] == subesp_selecionada]  # Alterado aqui
            print(f"[INFO] Número de OPs filtradas para a subespécie {subesp_selecionada}: {len(ops_disponiveis)}")

        # Passo 5: Seleção da OP para conferência
        print("\n=== OPs disponíveis ===")
        for idx, op in enumerate(ops_disponiveis['CODIGO_OP'].unique(), 1):
            produto = ops_disponiveis[ops_disponiveis['CODIGO_OP'] == op]['NOME_PRODUTO'].iloc[0]
            qtd = ops_disponiveis[ops_disponiveis['CODIGO_OP'] == op]['QTD_PREVISTA'].iloc[0]
            print(f"[{idx}] OP: {op} | Produto: {produto} | Qtde: {qtd}")

        op_escolhida = int(input(f"Digite o número da OP para iniciar conferência ou 0 para pular: "))
        if op_escolhida == 0:
            print("[OK] Ignorando OP.")
            continue

        op_selecionada = ops_disponiveis.iloc[op_escolhida - 1]
        cod_op = op_selecionada['CODIGO_OP']
        produto = op_selecionada['NOME_PRODUTO']
        qtd_prevista = op_selecionada['QTD_PREVISTA']

        print(f"[OK] OP selecionada: {cod_op} | Produto: {produto} | Qtde: {qtd_prevista}")

        # Registrar a OP no banco
        if not registrar_op(cod_op, produto, qtd_prevista):
            print("[ERRO] Falha ao registrar OP.")
            continue

        # Passo 6: Leitura do código de barras
        qtd_registrada = 0
        while qtd_registrada < qtd_prevista:
            codigo_barras = input(f"Digite ou escaneie o código de barras do produto (ou 'sair' para encerrar): ")
            if codigo_barras.lower() == "sair":
                print("[INFO] Encerrando conferência.")
                break

            # Verificar se o código de barras é válido
            if registrar_leitura(codigo_barras, cod_op, qtd_prevista):
                qtd_registrada += 1
                print(f"[INFO] {qtd_registrada}/{qtd_prevista} registrados.")
            else:
                print("[ERRO] Código de barras inválido ou já registrado.")

            if qtd_registrada >= qtd_prevista:
                print(f"[INFO] Quantidade máxima de {qtd_prevista} já registrada para esta OP.")
                break

if __name__ == "__main__":
    main()
