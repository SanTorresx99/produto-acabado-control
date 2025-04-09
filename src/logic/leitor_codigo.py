from datetime import datetime
import csv
from pathlib import Path

# Caminho onde os apontamentos serão salvos
APONTAMENTOS_PATH = Path("data/apontamentos.csv")
APONTAMENTOS_PATH.parent.mkdir(parents=True, exist_ok=True)

def registrar_leitura(codigo_barras: str, op_codigo: str = "", id_produto: int = 0, nome_produto: str = ""):
    """
    Registra uma leitura de código de barras com data/hora atual e ID Sequencial.
    Parâmetros:
        codigo_barras (str): Código de barras lido (via scanner ou digitado)
        op_codigo (str): Código da ordem de produção (opcional)
        id_produto (int): ID do produto (opcional)
        nome_produto (str): Nome do produto (opcional)
    """
    agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Recupera o último ID de leitura (incrementa a partir disso)
    if APONTAMENTOS_PATH.exists():
        with open(APONTAMENTOS_PATH, mode="r", encoding="utf-8") as f:
            linhas = list(csv.reader(f))
            id_leitura = int(linhas[-1][0]) if len(linhas) > 1 else 0
    else:
        id_leitura = 0

    novo_id = id_leitura + 1
    linha = [novo_id, agora, codigo_barras, op_codigo, id_produto, nome_produto]

    escrever_cabecalho = not APONTAMENTOS_PATH.exists()
    with open(APONTAMENTOS_PATH, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if escrever_cabecalho:
            writer.writerow(["id_leitura", "data_hora", "codigo_barras", "codigo_op", "id_produto", "nome_produto"])
        writer.writerow(linha)

    print(f"[OK] Leitura registrada: ID={novo_id} | Código: {codigo_barras} | Hora: {agora}")
