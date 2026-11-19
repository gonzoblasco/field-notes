"""Interviewer agent: turns a coverage gap into the next question."""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List

import ollama

MODEL = os.environ.get("FIELD_NOTES_MODEL", "qwen3:4b-instruct-2507-q4_K_M")
LANGUAGE = os.environ.get("FIELD_NOTES_LANG", "en")

_SYSTEM = (
    "You are an interviewer helping an older person tell their life story. "
    "You receive the gaps in an interview so far and you propose ONE follow-up question. "
    "Rules: warm and respectful tone; one open, concrete question; never give advice and never interpret; "
    "never invent details the person did not say. "
    "Return JSON with: pregunta (str), categoria (str), por_que (str, max 20 words)."
)


def _prompt(huecos: List[Dict[str, Any]], contexto: str) -> str:
    huecos_txt = "\n".join(f"- {h['categoria']}: {h['descripcion']}" for h in huecos)
    return (
        f"What the person has already told us (verbatim excerpt):\n{contexto}\n\n"
        f"Themes that have not come up:\n{huecos_txt}\n\n"
        "Pick the gap that matters most for a life story and propose the next question."
    )


def propose_question(huecos: List[Dict[str, Any]], segmentos: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Return {pregunta, categoria, por_que} grounded in the detected gaps."""
    if not huecos:
        return {
            "pregunta": "Is there anything else you would like to tell me that I have not asked about?",
            "categoria": "cierre",
            "por_que": "no gaps left in the checklist",
        }

    contexto = " ".join(s.get("texto", "") for s in segmentos)[-1500:]
    resp = ollama.chat(
        model=MODEL,
        messages=[
            {"role": "system", "content": _SYSTEM},
            {"role": "user", "content": _prompt(huecos, contexto)},
        ],
        format="json",
        options={"num_ctx": 4096},
    )
    content = resp["message"]["content"]
    try:
        data = json.loads(content)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"The model did not return valid JSON: {content[:200]}") from exc

    pregunta = (data.get("pregunta") or "").strip()
    if not pregunta:
        raise RuntimeError("The model returned an empty question")

    categorias = {h["categoria"] for h in huecos}
    categoria = data.get("categoria") if data.get("categoria") in categorias else huecos[0]["categoria"]
    return {
        "pregunta": pregunta,
        "categoria": categoria,
        "por_que": (data.get("por_que") or "").strip()[:160],
    }
