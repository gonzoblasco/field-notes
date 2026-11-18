from unittest.mock import patch

from memori.oral.questions import propose_question

HUECOS = [
    {"categoria": "migración", "descripcion": "El relato no menciona nada de migración.", "cubierto": 0},
    {"categoria": "recuerdos", "descripcion": "El relato no menciona nada de recuerdos.", "cubierto": 0},
]
SEGMENTOS = [{"texto": "Nací en Bahía Blanca en el 42."}]


def _fake(payload: dict):
    import json

    return {"message": {"content": json.dumps(payload)}}


def test_propose_question_returns_structured():
    payload = {
        "pregunta": "¿Y cómo fue ese viaje desde Bahía Blanca hasta acá?",
        "categoria": "migración",
        "por_que": "no contó cómo llegó",
    }
    with patch("memori.oral.questions.ollama.chat", return_value=_fake(payload)):
        out = propose_question(HUECOS, SEGMENTOS)
    assert out["pregunta"].startswith("¿")
    assert out["categoria"] == "migración"
    assert out["por_que"]


def test_propose_question_without_gaps():
    out = propose_question([], SEGMENTOS)
    assert out["categoria"] == "cierre"
    assert out["pregunta"]
