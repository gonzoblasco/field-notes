"""Agente que propone la próxima pregunta a partir de los huecos."""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List

import ollama

MODEL = os.environ.get("MEMORIA_ORAL_MODEL", "qwen3:4b-instruct-2507-q4_K_M")

_SYSTEM = (
    "Sos un entrevistador que ayuda a una persona mayor a contar su historia. "
    "Recibís los huecos de una entrevista y proponés UNA sola pregunta de seguimiento. "
    "Reglas: español rioplatense con voseo; tono cálido y respetuoso; "
    "una pregunta abierta y concreta; nunca des consejos ni interpretes; "
    "nunca inventes datos que la persona no dijo. "
    "Devolvé JSON con: pregunta (str), categoria (str), por_que (str, máx 20 palabras).\n\n"
    "El voseo es obligatorio. Ejemplos del registro correcto:\n"
    "- ¿Qué recordás de tu barrio?\n"
    "- ¿Cómo era tu casa cuando eras chico?\n"
    "- ¿Tenés algún recuerdo de ese viaje?\n"
    "- ¿Qué hacías los domingos?\n"
    "Nunca uses 'tú', 'tienes', 'recuerdas', 'haces' ni 'eras' con 'tú'. "
    "Usá 'vos', 'tenés', 'recordás', 'hacés'."
)


def _prompt(huecos: List[Dict[str, Any]], contexto: str) -> str:
    huecos_txt = "\n".join(f"- {h['categoria']}: {h['descripcion']}" for h in huecos)
    return (
        f"Lo que la persona ya contó (resumen textual):\n{contexto}\n\n"
        f"Temas que no aparecieron:\n{huecos_txt}\n\n"
        "Elegí el hueco más importante para la historia de vida y proponé la próxima pregunta."
    )


def propose_question(huecos: List[Dict[str, Any]], segmentos: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Devuelve {pregunta, categoria, por_que} a partir de los huecos."""
    if not huecos:
        return {
            "pregunta": "¿Hay algo más que quieras contarme que no te haya preguntado?",
            "categoria": "cierre",
            "por_que": "no quedan huecos en el checklist",
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
        raise RuntimeError(f"El modelo no devolvió JSON válido: {content[:200]}") from exc

    pregunta = (data.get("pregunta") or "").strip()
    if not pregunta:
        raise RuntimeError("El modelo devolvió una pregunta vacía")

    categorias = {h["categoria"] for h in huecos}
    categoria = data.get("categoria") if data.get("categoria") in categorias else huecos[0]["categoria"]
    return {
        "pregunta": pregunta,
        "categoria": categoria,
        "por_que": (data.get("por_que") or "").strip()[:160],
    }
