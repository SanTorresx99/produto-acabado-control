# src/logic/validacoes.py

def validar_qtd(quantidade_registrada, qtd_prevista):
    """
    Valida se a quantidade registrada não excede a quantidade prevista.

    Parâmetros:
        quantidade_registrada (int ou float): A quantidade de produtos já conferidos.
        qtd_prevista (int ou float): A quantidade prevista para o produto.

    Retorna:
        bool: True se a quantidade registrada for válida (menor ou igual à prevista), False se exceder.
    """
    if quantidade_registrada > qtd_prevista:
        print(f"[ERRO] A quantidade registrada ({quantidade_registrada}) não pode exceder a prevista ({qtd_prevista}).")
        return False
    return True
