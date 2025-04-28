from database.conexao import conectar_novo_banco
import pandas as pd

def registrar_op(cod_op, nome_produto, qtd_prevista, especie, sub_especie, id_produto, cod_barras):
    """
    Registra a OP na tabela OPS no banco de controle.
    """
    conn = conectar_novo_banco()  # Usando a conexão com o banco de controle
    if not conn:
        return False

    try:
        # Verifica se a OP já está registrada
        sql_verificar_op = f"""
            SELECT COUNT(*) 
            FROM OPS 
            WHERE CODIGO_OP = '{cod_op}'
        """
        cursor = conn.cursor()
        cursor.execute(sql_verificar_op)
        count = cursor.fetchone()[0]

        # Se a OP não existe, insere na tabela
        if count == 0:
            sql_inserir_op = f"""
                INSERT INTO OPS (CODIGO_OP, NOME_PRODUTO, QTD_PREVISTA, DATA_PREVISTA, ESPECIE, SUB_ESPECIE, ID_PRODUTO, COD_BARRAS)
                VALUES ('{cod_op}', '{nome_produto}', {qtd_prevista}, CURRENT_TIMESTAMP, '{especie}', '{sub_especie}', {id_produto}, '{cod_barras}')
            """
            cursor.execute(sql_inserir_op)
            conn.commit()
            print(f"[OK] OP {cod_op} registrada com sucesso.")
        else:
            print(f"[INFO] OP {cod_op} já registrada.")
        return True
    except Exception as e:
        print(f"[ERRO] Falha ao registrar OP: {e}")
        return False
    finally:
        conn.close()

def verificar_codigo_pertencente_op(codigo_barras, cod_op):
    """
    Verifica se o código de barras pertence à OP selecionada no banco ERP.
    Retorna True se o código de barras pertencer à OP, e False caso contrário.
    """
    conn = conectar_novo_banco()  # Usando a conexão com o novo banco
    if not conn:
        return False

    try:
        sql_verificar = f"""
            SELECT COUNT(*) 
            FROM LEITURA_PRODUTO
            WHERE CODIGO_BARRAS = ? AND COD_OP = ?
        """
        cursor = conn.cursor()
        cursor.execute(sql_verificar, (codigo_barras, cod_op))
        count = cursor.fetchone()[0]
        return count == 0  # Se não encontrou o código de barras para a OP, retorna True
    except Exception as e:
        print(f"[ERRO] Falha ao verificar código de barras: {e}")
        return False
    finally:
        conn.close()

def registrar_leitura(codigo_barras, cod_op, qtd_prevista):
    """
    Registra a leitura do código de barras no banco de dados do projeto.
    Realiza as verificações se o código pertence à OP e a quantidade já registrada.
    """
    conn = conectar_novo_banco()  # Usando a conexão com o novo banco
    if not conn:
        return False

    try:
        # Passo 1: Verifica se o código de barras pertence à OP
        if not verificar_codigo_pertencente_op(codigo_barras, cod_op):
            print(f"[ERRO] O código de barras {codigo_barras} não pertence à OP {cod_op}.")
            return False

        # Passo 2: Verifica a quantidade registrada para essa OP
        sql_verificar_qtd = f"""
            SELECT COUNT(*) 
            FROM LEITURA_PRODUTO
            WHERE COD_OP = ? 
        """
        cursor = conn.cursor()
        cursor.execute(sql_verificar_qtd, (cod_op,))
        qtd_registrada = cursor.fetchone()[0]

        print(f"[INFO] Quantidade registrada: {qtd_registrada}/{qtd_prevista}")

        # Passo 3: Verifica se a quantidade registrada é menor que a prevista
        if qtd_registrada >= qtd_prevista:
            resposta = input(f"[ALERTA] A quantidade prevista ({qtd_prevista}) já foi atingida. Deseja continuar registrando (S/N)? ")
            if resposta.lower() != 's':
                print("[INFO] Parando a conferência.")
                return False

        # Passo 4: Registra o código de barras
        sql_inserir = f"""
            INSERT INTO LEITURA_PRODUTO (CODIGO_BARRAS, COD_OP, QUANTIDADE, STATUS)
            VALUES (?, ?, ?, 'Registrado')
        """
        cursor.execute(sql_inserir, (codigo_barras, cod_op, 1))
        conn.commit()
        print(f"[OK] Leitura registrada: Código de barras {codigo_barras} | OP {cod_op}")
        return True

    except Exception as e:
        print(f"[ERRO] Falha ao registrar leitura: {e}")
        return False
    finally:
        conn.close()