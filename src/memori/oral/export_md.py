"""Export de una entrevista a Markdown."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from .db import get_huecos, get_segmentos, list_entrevistas


def _ms(ms: int) -> str:
    total = int(ms) // 1000
    return f"{total // 60:02d}:{total % 60:02d}"


def _by_id(conn, entrevista_id: int) -> Dict[str, Any]:
    for e in list_entrevistas(conn):
        if e["id"] == entrevista_id:
            return dict(e)
    raise KeyError(f"No existe la entrevista {entrevista_id}")


def render_markdown(conn, entrevista_id: int, pregunta: Dict[str, Any] | None = None) -> str:
    e = _by_id(conn, entrevista_id)
    segmentos: List[Dict[str, Any]] = [dict(s) for s in get_segmentos(conn, entrevista_id)]
    huecos: List[Dict[str, Any]] = [dict(h) for h in get_huecos(conn, entrevista_id)]

    lines = [
        f"# {e['titulo']}",
        "",
        f"**Persona:** {e['persona'] or 'sin nombre'}  ",
        f"**Fecha:** {e['fecha'] or 'sin fecha'}  ",
        f"**Audio original:** `{e['audio_path'] or '—'}`",
        "",
        "> Transcripción local con whisper.cpp. La voz y el texto no salieron de esta máquina.",
        "",
        "## Relato",
        "",
    ]
    for s in segmentos:
        lines.append(f"**[{_ms(s['inicio_ms'])}–{_ms(s['fin_ms'])}]** {s['texto']}")
        lines.append("")

    if huecos:
        lines += ["## Temas que quedaron abiertos", ""]
        for h in huecos:
            lines.append(f"- **{h['categoria']}**: {h['descripcion']}")
        lines.append("")

    if pregunta:
        lines += [
            "## Próxima pregunta sugerida",
            "",
            f"> {pregunta['pregunta']}",
            "",
            f"_Motivo: {pregunta.get('por_que', 'hueco detectado')} (categoría {pregunta.get('categoria', '—')})_",
            "",
        ]

    lines += [
        "---",
        "",
        "Exportado por Memoria Oral. Este archivo se lee sin la app.",
        "",
    ]
    return "\n".join(lines)


def export_markdown(conn, entrevista_id: int, out_path: Path, pregunta: Dict[str, Any] | None = None) -> Path:
    text = render_markdown(conn, entrevista_id, pregunta)
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(text, encoding="utf-8")
    return out_path
