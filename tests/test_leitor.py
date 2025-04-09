import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from logic.leitor_codigo import registrar_leitura

def limpar_codigo_barras(texto: str) -> str:
    """
    Remove espaços e mantém apenas dígitos numéricos.
    Pode ser ajustado para tratar prefixos/sufixos de leitores.
    """
    return ''.join(filter(str.isdigit, texto.strip()))

try:
    # === ENTRADA MANUAL ===
    # Por enquanto, estamos utilizando input() padrão.
    # Quando o leitor estiver disponível, podemos trocar para sys.stdin.readline()
    codigo_raw = input("Digite o código de barras (ou cole manualmente): ")
    codigo = limpar_codigo_barras(codigo_raw)

    if not codigo:
        print("[!] Nenhum código válido informado.")
        sys.exit(1)

    op = input("Informe o código da OP (opcional): ").strip()
    id_prod = input("Informe o ID do produto (opcional): ").strip()
    nome = input("Informe o nome do produto (opcional): ").strip()

    registrar_leitura(
        codigo_barras=codigo,
        op_codigo=op,
        id_produto=int(id_prod) if id_prod else 0,
        nome_produto=nome
    )

except KeyboardInterrupt:
    print("\n[!] Leitura manual cancelada pelo usuário.")