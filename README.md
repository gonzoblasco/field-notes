# Memoria Oral — historia familiar local

Un agente que graba entrevistas, las transcribe **100 % en tu máquina**, detecta los huecos del relato y te hace la siguiente pregunta. Las voces no salen a ningún servidor.

> **Consentimiento antes que código.** La persona entrevistada sabe qué se graba, dónde queda, quién lo puede escuchar y cómo se borra. Es **autora** del relato, no sujeto. Un agente no reemplaza a un nieto.

## Qué hace

- Ingesta audio (wav/m4a) y lo transcribe localmente con timestamps.
- Guarda entrevistas y segmentos en SQLite.
- Compara el relato contra un **checklist de cobertura** (niñez, familia, trabajo, migración, recuerdos).
- Propone la próxima pregunta a partir de los huecos.
- Exporta la entrevista a Markdown, abrible sin la app.

## Stack

| Capa | Elección | Por qué |
|---|---|---|
| STT | whisper.cpp + `ggml-large-v3-turbo-q5_0` (547 MB) | MIT, ~4,8× tiempo real medido |
| LLM | Ollama + `qwen3:4b-instruct-2507-q4_K_M` (Apache-2.0) | 4B, instrucciones en español, licencia limpia |
| Store | SQLite + FTS5 | Reuso del motor de Nido |
| UI | HTML local en 127.0.0.1 | Sin Electron en 48 h |
| Lenguaje | Python 3.11+ | Ecosistema audio |

## Fuera de alcance

Diarización, app móvil, fine-tune, traducción, nube.

## Estado

Planificación. Ver `.knowledge/BRIEF.md` y el programa `memoria-oral` del Planner.
