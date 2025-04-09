import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from logic.consulta_ops import carregar_ops

# Teste básico
data = input("Escolha uma data no formato YYYY-MM-DD: ")
df = carregar_ops(data)
print(df.head())           # Mostra as 5 primeiras linhas
print(df.shape)            # Mostra quantas linhas e colunas vieram