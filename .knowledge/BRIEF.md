# BRIEF — Memoria Oral

## Objetivo
Construir un MVP que grabe entrevistas, las transcriba 100 % en local, detecte huecos en el relato y haga la siguiente pregunta, con export a Markdown.

## Por qué existe
Halloween y Día de los Muertos son el marco, pero el valor real es otro: las voces de una familia son irrecuperables y no pueden ir a un servidor. Una voz es única; si se filtra, no se puede cambiar como una contraseña.

## Principios aprobados por Gonzo (2026-11-18)
1. **Consentimiento antes que código.** Qué se graba, dónde queda, quién lo escucha, cómo se borra.
2. **La persona es autora del relato.** El export lleva su nombre y sus condiciones de uso.
3. **Un agente no reemplaza a un nieto.** El agente guía la conversación; el vínculo es humano.
4. **Nada de datos reales en el demo sin permiso explícito.**

## Stack decidido (brief de MIND, 2026-11-18)
- Python 3.11+
- whisper.cpp v1.9.5 con `ggml-large-v3-turbo-q5_0` (547 MB, MIT, ~4,8× tiempo real medido)
- Ollama + `qwen3:4b-instruct-2507-q4_K_M` (Apache-2.0; verificado via HF API el 2026-11-18)
- SQLite + FTS5 (+ `sqlite-vec` opcional)
- UI HTML local en `127.0.0.1`

## Alcance aprobado
- Ingesta de audio y transcripción local con timestamps.
- Store SQLite: entrevistas, segmentos, huecos.
- Checklist de cobertura configurable.
- Agente que propone la próxima pregunta.
- UI local de una pantalla.
- Export Markdown.
- Prueba de privacidad reproducible (`lsof`, 0 sockets).

## Fuera de alcance
Diarización, app móvil, fine-tune, traducción, nube.

## Definition of Done
- [ ] Audio real transcrito localmente con timestamps correctos.
- [ ] 0 sockets salientes durante la transcripción (evidencia pegada).
- [ ] Checklist detecta al menos 3 huecos reales en una entrevista.
- [ ] La pregunta propuesta cita el hueco que la motiva.
- [ ] Export Markdown se abre sin la app.
- [ ] `pytest` verde; `make demo` reproducible con audio sintético.

## Riesgos conocidos
- R1: audio real ≠ audio sintético (acento, ruido). Medir con grabación real.
- R2: agente genérico. Mitigación: checklist, no "mejor modelo".
- R3: ~~licencia de `gemma3:4b` sin verificar~~ → resuelto: se cambió a `qwen3:4b-instruct-2507`, Apache-2.0 verificada. `gemma3:4b` queda descartado por licencia (Gemma Terms, no OSI).

## Fuente
- Brief de viabilidad: `agents/kanam-mind/out/memoria-oral-feasibility.md`
- Mapa de los 5 challenges: `docs/challenges/hf26-map.md`
