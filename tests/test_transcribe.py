import shutil
from pathlib import Path

import pytest

from memori.oral.db import get_segmentos, init_db, list_entrevistas
from memori.oral.transcribe import transcribe_to_db

ROOT = Path(__file__).parents[1]
AUDIO = ROOT / "data" / "demo" / "entrevista-demo.wav"
MODEL = ROOT / "models" / "ggml-large-v3-turbo-q5_0.bin"


@pytest.mark.skipif(
    not shutil.which("whisper-cli") or not AUDIO.is_file() or not MODEL.is_file(),
    reason="whisper-cli, audio demo o modelo no disponibles",
)
def test_transcribe_demo(tmp_path):
    db = tmp_path / "test.db"
    result = transcribe_to_db(
        audio_path=AUDIO,
        db_path=db,
        model_path=MODEL,
        titulo="test",
        persona="demo",
    )
    assert result["segmentos"], "no se produjeron segmentos"
    conn = init_db(db)
    entrevistas = list_entrevistas(conn)
    assert len(entrevistas) == 1
    segs = get_segmentos(conn, entrevistas[0]["id"])
    assert len(segs) >= 1
    assert segs[0]["texto"].strip()
    assert segs[0]["fin_ms"] > segs[0]["inicio_ms"]
    conn.close()
