import sys
import os
import pandas as pd
from logic.consulta_ops import carregar_ops
from logic.leitor_codigo import registrar_leitura

def limpar_codigo_barras(texto: str) -> str:
    return ''.join(filter(str.isdigit, texto.strip()))

def selecionar_item(lista: list, titulo: str) -> str:
    print(f"\n=== {titulo.upper()} DISPONÍVEIS ===")
    for idx, item in enumerate(lista):
        print(f"[{idx}] {item}")
    while True:
        escolha = input(f"\nSelecione um {titulo.lower()}: ").strip()
        if escolha.isdigit() and int(escolha) in range(len(lista)):
            return lista[int(escolha)]
        else:
            print("[!] Opção inválida. Tente novamente.")

def selecionar_op(df_ops: pd.DataFrame) -> dict:
    print("\n=== OPs disponíveis ===")
    for idx, row in df_ops.iterrows():
        print(f"[{idx}] OP: {row['CODIGO_OP']} | Produto: {row['NOME_PRODUTO']} | Prevista: {row['DATA_PREVISTA']} | Qtde: {row['QTD_PREVISTA']}")
    while True:
        escolha = input("\nDigite o número da OP para iniciar conferência: ").strip()
        if escolha.isdigit() and int(escolha) in df_ops.index:
            return df_ops.loc[int(escolha)].to_dict()
        else:
            print("[!] Opção inválida. Tente novamente.")

def iniciar_contagem(op_selecionada: dict, df_filtrado: pd.DataFrame):
    print(f"\n>>> Iniciando leitura para OP {op_selecionada['CODIGO_OP']} | Produto: {op_selecionada['NOME_PRODUTO']}")
    print("Digite ou escaneie o código de barras (ou 'sair' para encerrar):\n")

    codigos_validos = df_filtrado[
        df_filtrado['CODIGO_OP'] == op_selecionada['CODIGO_OP']
    ]['CODIGO_BARRAS'].dropna().unique().tolist()

    quantidade_maxima = int(op_selecionada['QTD_PREVISTA']) or 0
    contador = 0

    while True:
        if contador >= quantidade_maxima:
            print(f"\n[⚠️] Limite de {quantidade_maxima} unidades atingido para esta OP.")
            break

        raw = input(f"[{contador+1}/{quantidade_maxima}] Código: ").strip()
        if raw.lower() == 'sair':
            print("Contagem encerrada pelo usuário.")
            break

        codigo = limpar_codigo_barras(raw)
        if not codigo:
            print("[!] Código inválido. Tente novamente.")
            continue

        if codigo not in codigos_validos:
            print(f"[!] Código {codigo} não pertence ao produto da OP selecionada.")
            continue

        registrar_leitura(
            codigo_barras=codigo,
            op_codigo=str(op_selecionada['CODIGO_OP']),
            id_produto=int(op_selecionada['ID_PRODUTO']),
            nome_produto=op_selecionada['NOME_PRODUTO']
        )
        contador += 1

def main():
    while True:
        print("\n=== SISTEMA DE APONTAMENTO DE PRODUÇÃO ===\n")
        data = input("Informe a data da OP (YYYY-MM-DD ou 'sair' para encerrar): ").strip()
        if data.lower() == 'sair':
            print("Encerrando o sistema.")
            break

        df_ops = carregar_ops(data)

        if df_ops.empty:
            print(f"[!] Nenhuma OP encontrada para {data}")
            continue

        especies = sorted(df_ops['ESPECIE'].dropna().unique().tolist())
        especie_sel = selecionar_item(especies, "espécie")

        df_filtrado = df_ops[df_ops['ESPECIE'] == especie_sel]

        subespecies = sorted(df_filtrado['SUB_ESPECIE'].dropna().unique().tolist())
        if subespecies:
            sub_sel = selecionar_item(subespecies, "subespécie")
            df_filtrado = df_filtrado[df_filtrado['SUB_ESPECIE'] == sub_sel]

        if df_filtrado.empty:
            print("[!] Nenhuma OP encontrada com os filtros aplicados.")
            continue

        df_filtrado.reset_index(drop=True, inplace=True)
        op = selecionar_op(df_filtrado)
        iniciar_contagem(op, df_filtrado)

if __name__ == "__main__":
    main()