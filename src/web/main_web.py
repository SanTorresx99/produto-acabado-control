from fastapi import FastAPI, Request, Form, Body
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
import pandas as pd
from datetime import datetime

from src.logic.usuario import autenticar_usuario
from src.logic.consulta_ops import carregar_ops_intervalo
from src.logic.leitor_codigo import REGISTROS_CSV_PATH, registrar_leitura

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
async def filtros_por_data(data: str):
    try:
        data_inicio = f"{data} 00:00:00"
        data_fim = f"{data} 23:59:59"
        df = carregar_ops_intervalo(data_inicio, data_fim)
        df.columns = df.columns.str.upper()

        subespecies = sorted(df["SUB_ESPECIE"].dropna().astype(str).unique().tolist())
        return JSONResponse({"subespecies": subespecies})
    except Exception as e:
        return JSONResponse({"erro": str(e), "subespecies": []})

@app.get("/api/ops")
async def listar_ops(data: str, subespecie: str = ""):
    try:
        data_inicio = f"{data} 00:00:00"
        data_fim = f"{data} 23:59:59"
        df_ops = carregar_ops_intervalo(data_inicio, data_fim)
        df_ops.columns = df_ops.columns.str.upper()

        df_ops["SUB_ESPECIE"] = df_ops["SUB_ESPECIE"].astype(str)
        df_ops["CODIGO_OP"] = df_ops["CODIGO_OP"].astype(str)

        if subespecie and subespecie.lower() != "todas":
            df_ops = df_ops[df_ops["SUB_ESPECIE"] == subespecie]

        if os.path.exists(REGISTROS_CSV_PATH):
            df_reg = pd.read_csv(REGISTROS_CSV_PATH, encoding="utf-8")
            df_reg.columns = df_reg.columns.str.upper()
            df_reg["COD_OP"] = df_reg["COD_OP"].astype(str)
            df_reg = df_reg[df_reg["COD_OP"].notna()]
            qtd_por_op = df_reg["COD_OP"].value_counts().to_dict()
        else:
            qtd_por_op = {}

        df_ops["QTD_REGISTRADA"] = df_ops["CODIGO_OP"].map(qtd_por_op).fillna(0).astype(int)

        for col in df_ops.select_dtypes(include=["datetime64[ns]", "datetime64[ns, UTC]"]):
            df_ops[col] = df_ops[col].astype(str)

        return JSONResponse({"ops": df_ops.to_dict(orient="records")})
    except Exception as e:
        return JSONResponse({"erro": str(e), "ops": []})

@app.get("/op/{cod_op}", response_class=HTMLResponse)
async def tela_apontamento_op(request: Request, cod_op: str):
    try:
        df = carregar_ops_intervalo("2025-01-01 00:00:00", "2999-12-31 23:59:59")
        df.columns = df.columns.map(str.upper)
        if "CODIGO_OP" in df.columns:
            df["CODIGO_OP"] = df["CODIGO_OP"].astype(str)
        else:
            return HTMLResponse(content=f"<h3>Coluna CODIGO_OP não encontrada no DataFrame.</h3>", status_code=500)

        dados_op = df[df["CODIGO_OP"] == cod_op].to_dict(orient="records")
        if not dados_op:
            return HTMLResponse(content="<h3>OP não encontrada.</h3>", status_code=404)

        dados_op = dados_op[0]

        if os.path.exists(REGISTROS_CSV_PATH):
            df_reg = pd.read_csv(REGISTROS_CSV_PATH, encoding="utf-8")
            df_reg.columns = df_reg.columns.str.upper()
            df_reg["COD_OP"] = df_reg["COD_OP"].astype(str)
            qtd_registrada = df_reg[df_reg["COD_OP"] == cod_op].shape[0]
        else:
            qtd_registrada = 0

        return templates.TemplateResponse("op_detalhe.html", {
            "request": request,
            "op": dados_op,
            "qtd_registrada": qtd_registrada
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return HTMLResponse(content=f"<h3>Erro ao carregar OP: {e}</h3>", status_code=500)

@app.post("/api/registrar_leitura")
async def api_registrar_leitura(dados: dict = Body(...)):
    try:
        sucesso = registrar_leitura(
            codigo_barras=dados.get("codigo_barras"),
            cod_op=dados.get("cod_op"),
            dados_op={
                "NOME_PRODUTO": dados.get("nome_produto"),
                "ESPECIE": dados.get("especie"),
                "SUB_ESPECIE": dados.get("sub_especie"),
                "ID_PRODUTO": dados.get("id_produto"),
                "CODIGO_BARRAS": dados.get("codigo_barras")
            }
        )
        if sucesso:
            return {"ok": True}
        return {"ok": False, "erro": "Código inválido para esta OP."}
    except Exception as e:
        return {"ok": False, "erro": str(e)}
