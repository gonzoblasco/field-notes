from unittest.mock import patch

from memori.oral.questions import propose_question

HUECOS = [
    {"categoria": "migration", "descripcion": "The story does not mention migration.", "cubierto": 0},
    {"categoria": "memories", "descripcion": "The story does not mention memories.", "cubierto": 0},
]
SEGMENTOS = [{"texto": "I was born in Bahia Blanca in 1942."}]


def _fake(payload: dict):
    import json

    return {"message": {"content": json.dumps(payload)}}


def test_propose_question_returns_structured():
    payload = {
        "pregunta": "How did you end up moving from Bahia Blanca to Buenos Aires?",
        "categoria": "migration",
        "por_que": "they never said how they got here",
    }
    with patch("memori.oral.questions.ollama.chat", return_value=_fake(payload)):
        out = propose_question(HUECOS, SEGMENTOS)
    assert out["pregunta"].endswith("?")
    assert out["categoria"] == "migration"
    assert out["por_que"]


def test_propose_question_without_gaps():
    out = propose_question([], SEGMENTOS)
    assert out["categoria"] == "cierre"
    assert out["pregunta"]
