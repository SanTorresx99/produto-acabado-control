from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
import pandas as pd
from datetime import datetime

from src.logic.usuario import autenticar_usuario
from src.logic.consulta_ops import carregar_ops_intervalo, filtrar_ops_por_esp_especie
from src.logic.leitor_codigo import REGISTROS_CSV_PATH

app = FastAPI()

# Diretório base do projeto
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))
static_path = os.path.join(BASE_DIR, "static")
if os.path.exists(static_path):
    app.mount("/static", StaticFiles(directory=static_path), name="static")

@app.get("/", response_class=HTMLResponse)
async def tela_login(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/login", response_class=HTMLResponse)
async def processa_login(request: Request, login: str = Form(...), senha: str = Form(...)):
    usuario = autenticar_usuario(login, senha)
    if usuario:
        if usuario["NIVEL_ACESSO"] == "admin":
            return RedirectResponse(url="/admin", status_code=302)
        return templates.TemplateResponse("dashboard.html", {"request": request, "usuario": usuario})
    return templates.TemplateResponse("index.html", {"request": request, "erro": "Login inválido."})

@app.get("/admin", response_class=HTMLResponse)
async def admin_dashboard(request: Request):
    try:
        data_str = request.query_params.get("data") or datetime.now().strftime('%Y-%m-%d')
        especie_filtro = (request.query_params.get("especie") or "").strip()
        subespecie_filtro = (request.query_params.get("subespecie") or "").strip()

        data_inicio = f"{data_str} 00:00:00"
        data_fim = f"{data_str} 23:59:59"

        df_ops = carregar_ops_intervalo(data_inicio, data_fim)
        df_ops.columns = df_ops.columns.str.upper()

        if df_ops.empty:
            return templates.TemplateResponse("admin_dashboard.html", {
                "request": request,
                "erro": f"Nenhuma OP encontrada para a data {data_str}.",
                "total_previsto": 0,
                "total_registrado": 0,
                "percentual": 0,
                "especie_detalhes": [],
                "data_selecionada": data_str,
                "especies": [],
                "subespecies": [],
                "especie_selecionada": especie_filtro,
                "subespecie_selecionada": subespecie_filtro,
                "ops_disponiveis": []
            })

        df_ops["COD_OP"] = df_ops["COD_OP"].astype(str)
        df_ops["QTD_PREVISTA"] = pd.to_numeric(df_ops["QTD_PREVISTA"], errors="coerce").fillna(0)

        especies = sorted(df_ops["ESPECIE"].dropna().unique().tolist())

        # Ajustando o filtro de espécie para garantir que as opções sejam mantidas
        if especie_filtro and especie_filtro != "todas":
            df_filtrado = filtrar_ops_por_esp_especie(df_ops.copy(), especie_filtro, "0")
            subespecies = sorted(df_filtrado["SUB_ESPECIE"].dropna().unique().tolist())
        else:
            subespecies = sorted(df_ops["SUB_ESPECIE"].dropna().unique().tolist())

        # Aplicando filtros conforme seleção
        if especie_filtro and especie_filtro != "todas":
            if subespecie_filtro and subespecie_filtro != "todas":
                df_ops = filtrar_ops_por_esp_especie(df_ops, especie_filtro, subespecie_filtro)
            else:
                df_ops = filtrar_ops_por_esp_especie(df_ops, especie_filtro, "0")

        # Processando registros
        if os.path.exists(REGISTROS_CSV_PATH):
            df_registros = pd.read_csv(REGISTROS_CSV_PATH)
            df_registros["COD_OP"] = df_registros["COD_OP"].astype(str)
            df_registros["QTD"] = pd.to_numeric(df_registros["QTD"], errors="coerce").fillna(0)
        else:
            df_registros = pd.DataFrame(columns=["COD_OP", "QTD"])

        df_merge = pd.merge(df_registros, df_ops[["COD_OP", "QTD_PREVISTA", "ESPECIE"]], on="COD_OP", how="inner")

        total_previsto = df_merge["QTD_PREVISTA"].sum()
        total_registrado = df_merge["QTD"].sum()
        percentual = round((total_registrado / total_previsto) * 100, 2) if total_previsto else 0

        especie_detalhes = (
            df_merge.groupby("ESPECIE").agg({"QTD": "sum", "QTD_PREVISTA": "sum"})
            .reset_index()
            .rename(columns={"QTD": "QTD_REGISTRADA"})
        )

        return templates.TemplateResponse("admin_dashboard.html", {
            "request": request,
            "total_previsto": total_previsto,
            "total_registrado": total_registrado,
            "percentual": percentual,
            "especie_detalhes": especie_detalhes.to_dict(orient="records"),
            "data_selecionada": data_str,
            "especies": especies,
            "subespecies": subespecies,
            "especie_selecionada": especie_filtro,
            "subespecie_selecionada": subespecie_filtro,
            "ops_disponiveis": df_ops.to_dict(orient="records")
        })

    except Exception as e:
        return templates.TemplateResponse("admin_dashboard.html", {
            "request": request,
            "erro": str(e),
            "total_previsto": 0,
            "total_registrado": 0,
            "percentual": 0,
            "especie_detalhes": [],
            "data_selecionada": datetime.now().strftime('%Y-%m-%d'),
            "especies": [],
            "subespecies": [],
            "especie_selecionada": None,
            "subespecie_selecionada": None,
            "ops_disponiveis": []
        })

@app.get("/op/{codigo_op}", response_class=HTMLResponse)
async def iniciar_registro_op(request: Request, codigo_op: str):
    try:
        # Buscar informações da OP selecionada para exibir mais detalhes
        df_ops = carregar_ops_intervalo(None, None)  # Carregar todas as OPs disponíveis
        df_ops.columns = df_ops.columns.str.upper()
        
        op_info = df_ops[df_ops["CODIGO_OP"] == codigo_op]
        
        if op_info.empty:
            return templates.TemplateResponse("op_registro.html", {
                "request": request, 
                "codigo_op": codigo_op,
                "erro": "OP não encontrada"
            })
            
        produto = op_info["NOME_PRODUTO"].iloc[0]
        qtd_prevista = op_info["QTD_PREVISTA"].iloc[0]
        
        # Verificar registros já feitos
        qtd_registrada = 0
        percentual_concluido = 0
        
        if os.path.exists(REGISTROS_CSV_PATH):
            df_registros = pd.read_csv(REGISTROS_CSV_PATH)
            registros_filtrados = df_registros[df_registros["COD_OP"] == codigo_op]
            qtd_registrada = len(registros_filtrados)
            percentual_concluido = round((qtd_registrada / qtd_prevista) * 100, 2) if qtd_prevista > 0 else 0
        
        return templates.TemplateResponse("op_registro.html", {
            "request": request,
            "codigo_op": codigo_op,
            "produto": produto,
            "qtd_prevista": qtd_prevista,
            "qtd_registrada": qtd_registrada,
            "percentual_concluido": percentual_concluido
        })
        
    except Exception as e:
        return templates.TemplateResponse("op_registro.html", {
            "request": request, 
            "codigo_op": codigo_op,
            "erro": str(e)
        })

@app.post("/op/{codigo_op}/registrar", response_class=HTMLResponse)
async def registrar_leitura(request: Request, codigo_op: str, codigo_barras: str = Form(...)):
    from src.logic.leitor_codigo import registrar_leitura
    
    try:
        # Buscar informações da OP para passar ao registrador
        df_ops = carregar_ops_intervalo(None, None)
        df_ops.columns = df_ops.columns.str.upper()
        
        op_info = df_ops[df_ops["CODIGO_OP"] == codigo_op]
        if op_info.empty:
            return templates.TemplateResponse("op_registro.html", {
                "request": request, 
                "codigo_op": codigo_op,
                "mensagem": "OP não encontrada",
                "sucesso": False
            })
            
        dados_op = op_info.iloc[0].to_dict()
        
        # Registrar a leitura
        sucesso = registrar_leitura(codigo_barras, codigo_op, dados_op)
        
        # Recalcular quantidade registrada
        qtd_registrada = 0
        percentual_concluido = 0
        qtd_prevista = dados_op.get("QTD_PREVISTA", 0)
        produto = dados_op.get("NOME_PRODUTO", "")
        
        if os.path.exists(REGISTROS_CSV_PATH):
            df_registros = pd.read_csv(REGISTROS_CSV_PATH)
            registros_filtrados = df_registros[df_registros["COD_OP"] == codigo_op]
            qtd_registrada = len(registros_filtrados)
            percentual_concluido = round((qtd_registrada / qtd_prevista) * 100, 2) if qtd_prevista > 0 else 0
        
        # Retornar o template com mensagem de sucesso ou erro
        return templates.TemplateResponse("op_registro.html", {
            "request": request,
            "codigo_op": codigo_op,
            "produto": produto,
            "qtd_prevista": qtd_prevista,
            "qtd_registrada": qtd_registrada,
            "percentual_concluido": percentual_concluido,
            "mensagem": "Código registrado com sucesso!" if sucesso else "Erro ao registrar código. Verifique se é válido ou já foi registrado.",
            "sucesso": sucesso
        })
        
    except Exception as e:
        return templates.TemplateResponse("op_registro.html", {
            "request": request, 
            "codigo_op": codigo_op,
            "mensagem": f"Erro: {str(e)}",
            "sucesso": False
        })

@app.get("/api/filtros")
async def filtros_por_data(data: str, especie: str = ""):
    try:
        data_inicio = f"{data} 00:00:00"
        data_fim = f"{data} 23:59:59"
        df = carregar_ops_intervalo(data_inicio, data_fim)
        df.columns = df.columns.str.upper()

        # Mantemos todas as espécies disponíveis independente do filtro
        especies = sorted(df["ESPECIE"].dropna().unique().tolist())
        
        # Filtramos as subespécies conforme a espécie selecionada
        if especie and especie.lower() != "todas":
            df_filtrado = df[df["ESPECIE"] == especie.strip()]
            subespecies = sorted(df_filtrado["SUB_ESPECIE"].dropna().unique().tolist())
        else:
            subespecies = sorted(df["SUB_ESPECIE"].dropna().unique().tolist())

        return JSONResponse({"especies": especies, "subespecies": subespecies})

    except Exception as e:
        return JSONResponse({"erro": str(e), "especies": [], "subespecies": []})