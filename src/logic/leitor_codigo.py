# src/logic/leitor_codigo.py
from database.conexao import conectar_novo_banco
import pandas as pd

def registrar_op(cod_op, nome_produto, qtd_prevista):
    """
    Registra a OP na tabela OPS do banco de dados controle_pa.fdb.
    """
    conn = conectar_novo_banco()  # Usando a conexão com o banco
    if not conn:
        return False

    try:
        # Verificar se a OP já está registrada
        sql_verificar_op = f"""
            SELECT COUNT(*) FROM OPS WHERE CODIGO_OP = ?
        """
        cursor = conn.cursor()
        cursor.execute(sql_verificar_op, (cod_op,))
        count = cursor.fetchone()[0]

        if count == 0:  # Se a OP não estiver registrada, vamos registrá-la
            sql_inserir_op = f"""
                INSERT INTO OPS (CODIGO_OP, NOME_PRODUTO, QTD_PREVISTA, STATUS, COD_BARRAS)
                VALUES (?, ?, ?, 'PENDENTE', ?)
            """
            cursor.execute(sql_inserir_op, (cod_op, nome_produto, qtd_prevista, ''))  # Inserir sem código de barras inicialmente
            conn.commit()
            print(f"[OK] OP {cod_op} registrada no banco.")
        else:
            print(f"[INFO] OP {cod_op} já está registrada.")

        return True

    except Exception as e:
        print(f"[ERRO] Falha ao registrar OP: {e}")
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
        # Passo 1: Verifica se a OP foi registrada, caso contrário, registra
        if not registrar_op(cod_op, "", qtd_prevista):
            print("[ERRO] OP não registrada. Abortando.")
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
