"""Transcripción local con whisper.cpp."""

from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict, List

from .db import init_db, insert_entrevista, insert_segmento

DEFAULT_MODEL = Path("models/ggml-large-v3-turbo-q5_0.bin")


def convert_to_wav(src: Path, dst: Path) -> Path:
    """Convierte a WAV 16 kHz mono usando afconvert (macOS)."""
    if src.suffix.lower() == ".wav":
        return src
    dst.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["afconvert", "-f", "WAVE", "-d", "LEI16@16000", str(src), str(dst)],
        check=True,
        capture_output=True,
    )
    return dst


def run_whisper(
    wav_path: Path,
    model_path: Path = DEFAULT_MODEL,
    language: str = "es",
) -> Dict[str, Any]:
    """Corre whisper-cli y devuelve el JSON parseado."""
    if not shutil.which("whisper-cli"):
        raise RuntimeError("whisper-cli no está instalado (brew install whisper.cpp)")
    if not model_path.is_file():
        raise RuntimeError(f"No existe el modelo: {model_path}")

    with tempfile.TemporaryDirectory() as tmp:
        prefix = Path(tmp) / "out"
        proc = subprocess.run(
            [
                "whisper-cli",
                "-m", str(model_path),
                "-f", str(wav_path),
                "-l", language,
                "-oj",
                "-of", str(prefix),
            ],
            capture_output=True,
            text=True,
        )
        if proc.returncode != 0:
            raise RuntimeError(f"whisper-cli falló: {proc.stderr[-500:]}")
        return json.loads(prefix.with_suffix(".json").read_text(encoding="utf-8"))


def _segments(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    out = []
    for item in payload.get("transcription", []):
        text = (item.get("text") or "").strip()
        if not text:
            continue
        offsets = item.get("offsets") or {}
        out.append(
            {
                "inicio_ms": int(offsets.get("from", 0)),
                "fin_ms": int(offsets.get("to", 0)),
                "texto": text,
            }
        )
    return out


def transcribe_to_db(
    audio_path: Path,
    db_path: Path,
    model_path: Path = DEFAULT_MODEL,
    titulo: str = "Entrevista",
    persona: str = "",
    language: str = "es",
) -> Dict[str, Any]:
    """Transcribe el audio y lo guarda en la DB. Devuelve la entrevista + segmentos."""
    audio_path = Path(audio_path)
    wav = convert_to_wav(audio_path, audio_path.with_suffix(".16k.wav"))
    payload = run_whisper(wav, Path(model_path), language)
    segments = _segments(payload)
    if not segments:
        raise RuntimeError("whisper no devolvió segmentos con texto")

    conn = init_db(db_path)
    entrevista_id = insert_entrevista(
        conn,
        titulo=titulo,
        audio_path=str(audio_path),
        fecha=None,
        persona=persona,
        consentimiento=0,
    )
    for seg in segments:
        insert_segmento(
            conn,
            entrevista_id=entrevista_id,
            inicio_ms=seg["inicio_ms"],
            fin_ms=seg["fin_ms"],
            texto=seg["texto"],
        )
    conn.close()
    return {"entrevista_id": entrevista_id, "segmentos": segments}


def main() -> None:
    import sys

    audio = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("data/demo/entrevista-demo.wav")
    result = transcribe_to_db(
        audio_path=audio,
        db_path=Path("data/index.db"),
        titulo=audio.stem,
        persona="Demo",
    )
    print(f"Entrevista #{result['entrevista_id']}: {len(result['segmentos'])} segmentos")
    for seg in result["segmentos"]:
        print(f"  [{seg['inicio_ms']}ms - {seg['fin_ms']}ms] {seg['texto']}")


if __name__ == "__main__":
    main()
