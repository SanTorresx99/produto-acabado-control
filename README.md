# 🧾 Admin Dashboard - Sistema de Apontamento de Produção#
Este projeto é uma interface web para conferência e controle de produção em uma fábrica de estofados e colchões. Desenvolvido em Python (FastAPI) e JavaScript puro, ele permite:

## ✅ Visualizar OPs por filtros de período, produto, subespécie e tipo

## 🧮 Verificar quantidade prevista × registrada

## 🧠 Apresentar status inteligentes de conferência

## 🛠️ Realizar apontamentos por leitor de código de barras

## 📁 Estrutura do Projeto

```bash
📦 produto-acabado-control/
├── backend/
│   └── main_web.py                # API e servidor FastAPI
├── frontend/
│   ├── templates/
│   │   └── admin_dashboard.html   # Tela principal da interface
|   |   └── index.html             # Tela de Login do usuário
|   |   └── op_detalhe.html        # Tela para leitura do código de barras
│   ├── static/
│   │   ├── css/style.css          # Estilos visuais
│   │   └── js/script.js           # Lógica da interface e paginação
├── files/
│   └── registros.csv              # Registros lidos pelo usuário
|   └── usuarios.csv               # Cadastro de logins, usuários e senhas 
├── .env                           # Configurações sensíveis
└── README.md                      # Você está aqui
```
### 🔧 Funcionalidades Implementadas
Funcionalidade	Descrição
### 🔎 Filtros de data, OP, produto, subespécie	Com validação entre datas
### 📅 Flatpickr com data em pt-BR	Integração dinâmica no calendário
### 🧾 Leitura e registro via API	Salvando no registros.csv
### 👤 Registro do usuário logado	Via cookie usuario
### 📊 Status visuais de conferência	✅ OK, ⚠️ a maior, 🔴 pendente, etc
### 🏭 Ícone de tipo de OP (linha/sob encomenda)	🏭 ou 🪡 na tabela
### 📌 Ordenação de OPs	Status > Subespécie > ID Produto
 
### 🚀 Como rodar
Crie o ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate  # ou .\\venv\\Scripts\\activate no Windows
```
```bash
Instale os requisitos:
pip install -r requisitos.txt
```
```bash
Execute o servidor:
uvicorn src.main_web:app --reload
```
Acesse no navegador:
http://127.0.0.1:8000

## 🔐 Acesso
Tela de login protegida por autenticação
Usuários cadastrados diretamente via lógica autenticar_usuario()

## 📌 Próximas melhorias (sugestões)
 Exportação para CSV da tabela

 Filtro por status diretamente na interface

 Legendas explicativas dos ícones

 Modularização do JavaScript
 
 Paginação de OPs 
