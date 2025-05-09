from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
from datetime import datetime
import os
import pandas as pd

from src.logic.usuario import autenticar_usuario
from src.logic.consulta_ops import carregar_ops_intervalo
from src.logic.leitor_codigo import registrar_leitura, buscar_dados_op

load_dotenv()
app = FastAPI()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "web", "templates"))
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "web", "static")), name="static")

# Cache temporário
df_ops_cache = pd.DataFrame()

@app.get("/", response_class=HTMLResponse)
async def tela_login(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/login", response_class=HTMLResponse)
async def processa_login(request: Request, login: str = Form(...), senha: str = Form(...)):
    if autenticar_usuario(login, senha):
        response = RedirectResponse(url="/admin", status_code=302)
        response.set_cookie(key="usuario", value=login)
        return response
    return templates.TemplateResponse("index.html", {"request": request, "erro": "Login inválido"})

@app.get("/admin", response_class=HTMLResponse)
async def painel_admin(request: Request):
    return templates.TemplateResponse("admin_dashboard.html", {"request": request})

@app.get("/api/filtros")
async def filtros_por_data(data_inicio: str, data_fim: str, tipo_op: str = "ambos"):
    try:
        data_inicio_fmt = datetime.strptime(data_inicio, "%d/%m/%Y").strftime("%Y-%m-%d")
        data_fim_fmt = datetime.strptime(data_fim, "%d/%m/%Y").strftime("%Y-%m-%d")
        df = carregar_ops_intervalo(data_inicio_fmt, data_fim_fmt, tipo_op=tipo_op)
        df.columns = df.columns.str.upper()
        subespecies = sorted(df['SUB_ESPECIE'].dropna().unique().tolist())
        return {"subespecies": subespecies}
    except Exception as e:
        return JSONResponse(status_code=500, content={"erro": str(e)})

@app.get("/api/ops")
async def dados_ops(
    data_inicio: str,
    data_fim: str,
    subespecie: str = "todas",
    id_produto: str = "",
    cod_op: str = "",
    tipo_op: str = "ambos"
):
    global df_ops_cache
    try:
        print("[INFO] Início da função /api/ops")
        data_inicio_fmt = datetime.strptime(data_inicio, "%d/%m/%Y").strftime("%Y-%m-%d")
        data_fim_fmt = datetime.strptime(data_fim, "%d/%m/%Y").strftime("%Y-%m-%d")
        codigos_op = [c.strip() for c in cod_op.split(",") if c.strip()] if cod_op else None

        df = carregar_ops_intervalo(data_inicio_fmt, data_fim_fmt, codigos_op=codigos_op, tipo_op=tipo_op)
        df.columns = df.columns.str.upper()

        if subespecie.lower() != "todas":
            df = df[df["SUB_ESPECIE"].str.upper() == subespecie.upper()]
        if id_produto:
            df = df[df["ID_PRODUTO"].astype(str) == str(id_produto)]

        df_ops_cache = df.copy()
        print(f"[INFO] {len(df)} OPs carregadas")
        return {"ops": df.to_dict(orient="records")}
    except Exception as e:
        print("[ERRO] Falha em /api/ops:", e)
        return JSONResponse(status_code=500, content={"erro": str(e)})

@app.get("/op/{codigo_op}", response_class=HTMLResponse)
async def tela_op(request: Request, codigo_op: str):
    try:
        global df_ops_cache
        if df_ops_cache.empty:
            df_ops_cache = carregar_ops_intervalo("2020-01-01", "2030-12-31")

        dados = buscar_dados_op(codigo_op, df_ops_cache)
        if not dados:
            return HTMLResponse(content="OP não encontrada", status_code=404)

        return templates.TemplateResponse("op_detalhe.html", {
            "request": request,
            "op": codigo_op,
            "produto": dados.get("NOME_PRODUTO"),
            "quantidade_prevista": dados.get("QTD_PREVISTA", 0),
            "quantidade_registrada": dados.get("QTD_REGISTRADA", 0),
            "erro": request.query_params.get("erro", "")
        })
    except Exception as e:
        return HTMLResponse(content=f"Erro interno: {e}", status_code=500)

@app.post("/op/{codigo_op}/registrar", response_class=RedirectResponse)
async def registrar_codigo_op(request: Request, codigo_op: str, codigo_barras: str = Form(...)):
    try:
        global df_ops_cache
        dados = buscar_dados_op(codigo_op, df_ops_cache)
        if not dados:
            return RedirectResponse(url=f"/op/{codigo_op}?erro=OP não encontrada", status_code=302)

        codigo_esperado = str(dados.get("COD_BARRAS")).strip()
        if codigo_barras.strip() != codigo_esperado:
            return RedirectResponse(url=f"/op/{codigo_op}?erro=Código de barras inválido para esta OP!", status_code=302)

        registrar_leitura(codigo_op, codigo_barras)
        return RedirectResponse(url=f"/op/{codigo_op}", status_code=302)
    except Exception as e:
        return HTMLResponse(content=f"Erro ao registrar: {e}", status_code=500)
