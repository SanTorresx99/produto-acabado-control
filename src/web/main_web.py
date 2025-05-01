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
async def admin_page(request: Request):
    return templates.TemplateResponse("admin_dashboard.html", {"request": request})

@app.get("/api/filtros")
async def filtros_por_data(data: str, especie: str = "", subespecie: str = ""):
    try:
        data_inicio = f"{data} 00:00:00"
        data_fim = f"{data} 23:59:59"
        df = carregar_ops_intervalo(data_inicio, data_fim)
        df.columns = df.columns.str.upper()

        especies = sorted(df["ESPECIE"].dropna().unique().tolist())
        subespecies = sorted(df["SUB_ESPECIE"].dropna().unique().tolist())

        if especie and especie.lower() != "todas":
            df = df[df["ESPECIE"] == especie.strip()]
            subespecies = sorted(df["SUB_ESPECIE"].dropna().unique().tolist())

        if subespecie and subespecie.lower() != "todas":
            df = df[df["SUB_ESPECIE"] == subespecie.strip()]
            especies = sorted(df["ESPECIE"].dropna().unique().tolist())

        return JSONResponse({"especies": especies, "subespecies": subespecies})

    except Exception as e:
        return JSONResponse({"erro": str(e), "especies": [], "subespecies": []})

@app.get("/api/especie_por_subespecie")
async def obter_especie_por_subespecie(subespecie: str):
    try:
        df = carregar_ops_intervalo(None, None)
        df.columns = df.columns.str.upper()
        especie = df[df["SUB_ESPECIE"] == subespecie]["ESPECIE"].dropna().unique()
        if len(especie) > 0:
            return JSONResponse({"especie": especie[0]})
        return JSONResponse({"especie": ""})
    except Exception as e:
        return JSONResponse({"erro": str(e), "especie": ""})

@app.get("/api/ops")
async def listar_ops(data: str, especie: str = "", subespecie: str = ""):
    try:
        data_inicio = f"{data} 00:00:00"
        data_fim = f"{data} 23:59:59"
        df_ops = carregar_ops_intervalo(data_inicio, data_fim)
        df_ops.columns = df_ops.columns.str.upper()

        if especie and especie.lower() != "todas":
            df_ops = df_ops[df_ops["ESPECIE"] == especie]

        if subespecie and subespecie.lower() != "todas":
            df_ops = df_ops[df_ops["SUB_ESPECIE"] == subespecie]

        return JSONResponse({"ops": df_ops.to_dict(orient="records")})
    except Exception as e:
        return JSONResponse({"erro": str(e), "ops": []})
