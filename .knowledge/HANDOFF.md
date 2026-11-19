# HANDOFF — Memoria Oral

## Estado: MVP cerrado, repo publico

- Repo: https://github.com/gonzoblasco/memoria-oral (MIT, publico)
- Programa `memoria-oral`: 9/9 pasos cerrados. 8 tests verdes.
- Stack: whisper.cpp 1.9.5 + ggml-large-v3-turbo-q5_0 (547 MB) + Ollama + qwen3:4b-instruct-2507 (Apache-2.0) + SQLite/FTS5 + FastAPI.

## Verificado

- Audio 7.1 s -> 1.63 s de computo (4.4x tiempo real).
- Timestamps 0-6760 ms contra afinfo 7.125 s (el resto es silencio).
- 9 muestras de `lsof`: 0 conexiones durante la transcripcion.
- Consentimiento: POST /transcribe sin checkbox devuelve 400.

## Deuda abierta

1. Voseo inconsistente en el modelo 4B (2 fallas, 1 acierto). Mitigacion: mas ejemplos en el prompt o fine-tune.
2. Audio demo es sintetico (`say -v Paulina`). Falta una entrevista real con permiso.
3. Consentimiento es un checkbox, no una firma.
4. i18n opcion A pendiente (es/en en UI y en el prompt del entrevistador).

## Como retomar

```bash
cd projects/memoria-oral
uv sync
uv run pytest -q
PYTHONPATH=src uv run uvicorn memori.oral.ui:app --port 8100
```
