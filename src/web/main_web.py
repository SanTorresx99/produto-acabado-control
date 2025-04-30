from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
import pandas as pd
from datetime import datetime

from src.logic.usuario import autenticar_usuario
from src.logic.consulta_ops import carregar_ops, filtrar_ops_por_esp_especie
from src.logic.leitor_codigo import REGISTROS_CSV_PATH

app = FastAPI()

# Diretório base do projeto
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

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
        especie_filtro = request.query_params.get("especie") or ""
        subespecie_filtro = request.query_params.get("subespecie") or ""

        df_ops = carregar_ops(data_str)
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
                "subespecie_selecionada": subespecie_filtro
            })

        df_ops["COD_OP"] = df_ops["COD_OP"].astype(str)
        df_ops["QTD_PREVISTA"] = pd.to_numeric(df_ops["QTD_PREVISTA"], errors="coerce").fillna(0)

        especies = sorted(df_ops["ESPECIE"].dropna().unique().tolist())
        subespecies = []

        if especie_filtro and especie_filtro != "todas":
            df_ops = filtrar_ops_por_esp_especie(df_ops, especie_filtro, "0")
            subespecies = sorted(df_ops["SUB_ESPECIE"].dropna().unique().tolist())

        if subespecie_filtro and subespecie_filtro != "todas":
            df_ops = filtrar_ops_por_esp_especie(df_ops, especie_filtro, subespecie_filtro)

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
            "subespecie_selecionada": subespecie_filtro
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
            "subespecie_selecionada": None
        })
