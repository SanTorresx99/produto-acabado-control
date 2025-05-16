from fastapi import FastAPI, Request, Form, Body
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
from datetime import datetime
import os
import pandas as pd

from src.logic.usuario import autenticar_usuario
from src.logic.consulta_ops import carregar_ops_intervalo

# 🕽 Load env
load_dotenv()

# 🕽 Inicializa app
app = FastAPI()

# 🕽 Caminhos
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
# 📟 Painel Admin
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

        ops = df.fillna(0).to_dict(orient="records")
        df = df.replace({pd.NA: None, float("nan"): 0})
        return {"ops": ops}

    except Exception as e:
        print("[ERRO] Falha em /api/ops:", e)
        return JSONResponse(status_code=500, content={"erro": str(e)})

# ===========================
# 📄 Página Detalhe da OP
# ===========================
@app.get("/op/{cod_op}", response_class=HTMLResponse)
async def detalhe_op(request: Request, cod_op: str):
    try:
        df = carregar_ops_intervalo("2025-01-01", "2025-12-31", tipo_op="ambos")
        df.columns = df.columns.str.upper()
        df = df[df["CODIGO_OP"].astype(str) == cod_op]

        if df.empty:
            return HTMLResponse(content=f"<h2>OP {cod_op} não encontrada.</h2>", status_code=404)

        op = df.iloc[0].to_dict()

        # Quantidade registrada no CSV (pode ser omitido se já vier do df)
        qtd_registrada = op.get("QTD_REGISTRADA", 0)

        return templates.TemplateResponse("op_detalhe.html", {
            "request": request,
            "op": op,
            "qtd_registrada": qtd_registrada
        })

    except Exception as e:
        return HTMLResponse(content=f"<h2>Erro ao carregar OP: {str(e)}</h2>", status_code=500)

# ===========================
# 📥 API - Registrar leitura
# ===========================
@app.post("/api/registrar_leitura")
async def registrar_leitura(payload: dict = Body(...)):
    try:
        cod_op = payload.get("cod_op")
        codigo_barras = payload.get("codigo_barras")
        nome_produto = payload.get("nome_produto")
        especie = payload.get("especie")
        sub_especie = payload.get("sub_especie")
        id_produto = payload.get("id_produto")

        if not all([cod_op, codigo_barras, nome_produto, especie, sub_especie, id_produto]):
            return JSONResponse(status_code=400, content={"erro": "Dados incompletos"})

        caminho_csv = os.path.join(BASE_DIR, "files", "registros.csv")

        # Carrega registros existentes
        if os.path.exists(caminho_csv):
            df = pd.read_csv(caminho_csv, sep=",", dtype=str)
        else:
            df = pd.DataFrame(columns=["DATA", "COD_OP", "CODIGO_BARRAS", "ID_PRODUTO", "NOME_PRODUTO", "ESPECIE", "SUB_ESPECIE", "QTD"])

        # Adiciona novo registro
        novo_registro = {
            "DATA": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "COD_OP": cod_op,
            "CODIGO_BARRAS": codigo_barras,
            "ID_PRODUTO": id_produto,
            "NOME_PRODUTO": nome_produto,
            "ESPECIE": especie,
            "SUB_ESPECIE": sub_especie,
            "QTD": "1"
        }

        df = pd.concat([df, pd.DataFrame([novo_registro])], ignore_index=True)
        df.to_csv(caminho_csv, index=False, sep=",")

        return {"ok": True}

    except Exception as e:
        return JSONResponse(status_code=500, content={"erro": str(e)})
