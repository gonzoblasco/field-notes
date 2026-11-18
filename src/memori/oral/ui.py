"""UI local de una pantalla para Memoria Oral."""

from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

from fastapi import FastAPI, File, Request, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from .checklist import coverage_report
from .db import get_huecos, get_segmentos, init_db, insert_hueco, list_entrevistas
from .export_md import export_markdown
from .questions import propose_question
from .transcribe import transcribe_to_db

BASE = Path(__file__).resolve().parents[3]
DATA = BASE / "data"
DB_PATH = DATA / "index.db"
MODEL = BASE / "models" / "ggml-large-v3-turbo-q5_0.bin"
OUTPUT = BASE / "output"

app = FastAPI(title="Memoria Oral")
templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))


def _conn():
    return init_db(DB_PATH)


def _entrevista(entrevista_id: int):
    conn = _conn()
    e = next((dict(x) for x in list_entrevistas(conn) if x["id"] == entrevista_id), None)
    if not e:
        conn.close()
        return None, [], [], conn
    segs = [dict(s) for s in get_segmentos(conn, entrevista_id)]
    huecos = [dict(h) for h in get_huecos(conn, entrevista_id)]
    return e, segs, huecos, conn


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    conn = _conn()
    entrevistas = [dict(e) for e in list_entrevistas(conn)]
    conn.close()
    return HTMLResponse(
        templates.get_template("index.html").render(
            {"request": request, "entrevistas": entrevistas}
        )
    )


@app.post("/transcribe", response_class=HTMLResponse)
async def transcribe(request: Request, file: UploadFile = File(...), persona: str = ""):
    if not (shutil.which("whisper-cli") and MODEL.is_file()):
        return HTMLResponse(
            templates.get_template("error.html").render(
                {"request": request, "error": "whisper-cli o el modelo no están disponibles."}
            ),
            status_code=503,
        )
    DATA.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename or "audio.wav").suffix, dir=DATA) as tmp:
        tmp.write(await file.read())
        tmp_path = Path(tmp.name)
    result = transcribe_to_db(
        audio_path=tmp_path,
        db_path=DB_PATH,
        model_path=MODEL,
        titulo=Path(file.filename or "entrevista").stem,
        persona=persona or "sin nombre",
    )
    e, segs, huecos, conn = _entrevista(result["entrevista_id"])
    report = coverage_report(segs)
    for h in report["huecos"]:
        insert_hueco(conn, e["id"], h["categoria"], h["descripcion"], 0)
    conn.commit()
    conn.close()
    e, segs, huecos, conn = _entrevista(result["entrevista_id"])
    pregunta = propose_question(huecos, segs) if huecos else None
    conn.close()
    return HTMLResponse(
        templates.get_template("entrevista.html").render(
            {
                "request": request,
                "e": e,
                "segmentos": segs,
                "huecos": huecos,
                "report": report,
                "pregunta": pregunta,
            }
        )
    )


@app.get("/entrevista/{entrevista_id}", response_class=HTMLResponse)
async def ver(request: Request, entrevista_id: int):
    e, segs, huecos, conn = _entrevista(entrevista_id)
    if not e:
        conn.close()
        return HTMLResponse("No existe", status_code=404)
    report = coverage_report(segs)
    pregunta = propose_question(huecos, segs) if huecos else None
    conn.close()
    return HTMLResponse(
        templates.get_template("entrevista.html").render(
            {
                "request": request,
                "e": e,
                "segmentos": segs,
                "huecos": huecos,
                "report": report,
                "pregunta": pregunta,
            }
        )
    )


@app.post("/export/{entrevista_id}")
async def exportar(entrevista_id: int):
    e, segs, huecos, conn = _entrevista(entrevista_id)
    if not e:
        conn.close()
        return HTMLResponse("No existe", status_code=404)
    pregunta = propose_question(huecos, segs) if huecos else None
    path = export_markdown(conn, entrevista_id, OUTPUT / f"{e['titulo']}.md", pregunta)
    conn.close()
    return HTMLResponse(f"<p>Exportado en <code>{path}</code></p>")
