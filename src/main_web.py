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

# 🔽 Load env
load_dotenv()

# 🔽 Inicializa app
app = FastAPI()

# 🔽 Caminhos
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "web", "templates"))
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "web", "static")), name="static")

# ===========================
# 🔐 Tela de Login
# ===========================
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

# ===========================
# 🧾 Painel Admin
# ===========================
@app.get("/admin", response_class=HTMLResponse)
async def painel_admin(request: Request):
    return templates.TemplateResponse("admin_dashboard.html", {"request": request})

# ===========================
# 📊 API - Filtros
# ===========================
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

# ===========================
# 📊 API - Dados de OPs
# ===========================
@app.get("/api/ops")
async def dados_ops(
    data_inicio: str,
    data_fim: str,
    subespecie: str = "todas",
    id_produto: str = "",
    cod_op: str = "",
    tipo_op: str = "ambos"
):
    print("[INFO] Início da função /api/ops")
    try:
        data_inicio_fmt = datetime.strptime(data_inicio, "%d/%m/%Y").strftime("%Y-%m-%d")
        data_fim_fmt = datetime.strptime(data_fim, "%d/%m/%Y").strftime("%Y-%m-%d")

        df = carregar_ops_intervalo(data_inicio_fmt, data_fim_fmt, tipo_op=tipo_op)
        df.columns = df.columns.str.upper()
        print(f"[INFO] {len(df)} OPs carregadas")

        # Filtros adicionais
        if subespecie.lower() != "todas":
            df = df[df["SUB_ESPECIE"].str.upper() == subespecie.upper()]
        if id_produto:
            df = df[df["ID_PRODUTO"].astype(str) == str(id_produto)]
        if cod_op:
            codigos = [c.strip() for c in cod_op.split(",")]
            df = df[df["CODIGO_OP"].astype(str).isin(codigos)]

        # Carregar registros.csv
        caminho_csv = os.path.join(BASE_DIR, "files", "registros.csv")
        print(f"[INFO] Caminho do CSV: {caminho_csv}")
        if os.path.exists(caminho_csv):
            registros = pd.read_csv(caminho_csv, sep=",", dtype=str)
            registros["QTD"] = registros["QTD"].astype(int)
            registros["COD_OP"] = registros["COD_OP"].astype(str)
            print(f"[INFO] {len(registros)} linhas lidas do CSV")

            registros_agg = registros.groupby("COD_OP")["QTD"].sum().reset_index()
            registros_agg.rename(columns={"QTD": "QTD_REGISTRADA"}, inplace=True)

            df["CODIGO_OP"] = df["CODIGO_OP"].astype(str)
            df = df.merge(registros_agg, left_on="CODIGO_OP", right_on="COD_OP", how="left")

            # Verificação robusta
            if "QTD_REGISTRADA" not in df.columns:
                df["QTD_REGISTRADA"] = 0
            else:
                df["QTD_REGISTRADA"] = df["QTD_REGISTRADA"].fillna(0).astype(int)
        else:
            df["QTD_REGISTRADA"] = 0

        ops = df.fillna(0).to_dict(orient="records")
        df = df.replace({pd.NA: None, float("nan"): 0})
        return {"ops": ops}

    except Exception as e:
        print("[ERRO] Falha em /api/ops:", e)
        return JSONResponse(status_code=500, content={"erro": str(e)})
