"""Coverage checklist and gap detection for an interview."""

from __future__ import annotations

import re
from typing import Any, Dict, List

DEFAULT_CHECKLIST: Dict[str, List[str]] = {
    "childhood": ["childhood", "grew up", "born", "kid", "school", "neighborhood", "played"],
    "family": ["mother", "father", "mom", "dad", "brother", "sister", "grand", "family", "son", "daughter"],
    "work": ["work", "worked", "job", "trade", "factory", "shop", "office"],
    "migration": ["moved", "came from", "left", "town", "city", "arrived", "traveled"],
    "memories": ["remember", "recall", "miss", "happy", "sad", "proud"],
}


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip().lower()


def detect_gaps(
    segmentos: List[Dict[str, Any]],
    checklist: Dict[str, List[str]] | None = None,
) -> List[Dict[str, Any]]:
    """Return the checklist themes the story does not cover."""
    checklist = checklist or DEFAULT_CHECKLIST
    full = _normalize(" ".join(s.get("texto", "") for s in segmentos))
    gaps: List[Dict[str, Any]] = []
    for categoria, keywords in checklist.items():
        hits = [kw for kw in keywords if _normalize(kw) in full]
        if not hits:
            gaps.append(
                {
                    "categoria": categoria,
                    "descripcion": f"The story does not mention {categoria}.",
                    "cubierto": 0,
                }
            )
    return gaps


def coverage_report(
    segmentos: List[Dict[str, Any]],
    checklist: Dict[str, List[str]] | None = None,
) -> Dict[str, Any]:
    """Summary: covered themes, gaps and percentage."""
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
