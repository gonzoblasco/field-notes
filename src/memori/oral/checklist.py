"""Checklist de cobertura y detección de huecos en una entrevista."""

from __future__ import annotations

import re
from typing import Any, Dict, List

DEFAULT_CHECKLIST: Dict[str, List[str]] = {
    "niñez": ["infancia", "nací", "pibe", "chico", "escuela", "barrio", "juego"],
    "familia": ["mamá", "papá", "hermano", "hermana", "abuel", "familia", "hijo"],
    "trabajo": ["trabajo", "trabajaba", "oficio", "empleo", "fábrica", "taller"],
    "migración": ["viaje", "vinimos", "mudamos", "pueblo", "ciudad", "llegamos"],
    "recuerdos": ["recuerdo", "acuerdo", "extraño", "quiero", "feliz", "triste"],
}


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip().lower()


def detect_gaps(segmentos: List[Dict[str, Any]], checklist: Dict[str, List[str]] | None = None) -> List[Dict[str, Any]]:
    """Devuelve los temas del checklist que el relato no cubre.

    Un tema queda cubierto si alguna de sus palabras clave aparece en algún
    segmento. Los huecos se devuelven con la evidencia encontrada (si la hay).
    """
    checklist = checklist or DEFAULT_CHECKLIST
    full = _normalize(" ".join(s.get("texto", "") for s in segmentos))
    gaps: List[Dict[str, Any]] = []
    for categoria, keywords in checklist.items():
        hits = [kw for kw in keywords if _normalize(kw) in full]
        if not hits:
            gaps.append(
                {
                    "categoria": categoria,
                    "descripcion": f"El relato no menciona nada de {categoria}.",
                    "cubierto": 0,
                }
            )
    return gaps


def coverage_report(segmentos: List[Dict[str, Any]], checklist: Dict[str, List[str]] | None = None) -> Dict[str, Any]:
    """Resumen: temas cubiertos, huecos y porcentaje."""
    checklist = checklist or DEFAULT_CHECKLIST
    gaps = detect_gaps(segmentos, checklist)
    cubiertos = [c for c in checklist if c not in {g["categoria"] for g in gaps}]
    total = len(checklist)
    return {
        "total": total,
        "cubiertos": cubiertos,
        "huecos": gaps,
        "porcentaje": round(len(cubiertos) / total * 100, 1) if total else 0.0,
    }
