# produto-acabado-control
# 📦 produto-acabado-control

Sistema de controle de apontamento de produtos acabados, com leitura via código de barras, integrado ao banco de dados Firebird via Python.

## 🚀 Funcionalidades
- Seleção de Ordens de Produção (OP) a serem apontadas
- Leitura por código de barras (com data/hora da leitura)
- Validação de produto por OP
- Exportação de relatórios (CSV/Excel)
- Operação offline paralela ao ERP

## 🛠️ Tecnologias
- Python
- Firebird 3.0
- FastAPI (futuro)
- Docker
- pyodbc ou firebird-driver
- pandas

## 🔧 Como iniciar

```bash
# Crie o ambiente virtual
python -m venv venv
source venv/Scripts/activate  # Windows Git Bash
# ou
source venv/bin/activate      # Linux/WSL2

# Instale as dependências
pip install -r requirements.txt

# Configure o .env (baseado em .env.example)
