import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from logic.consulta_ops import carregar_ops

# Teste usando datas fictícias só pra passar pelo print
df = carregar_ops("2024-01-01", "2025-01-01")

print(df.head())
