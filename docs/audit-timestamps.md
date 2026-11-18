# Auditoría — Memoria Oral: timestamps y citas

**Auditor:** Kanam CORE (verificación directa contra archivos y binarios)
**Fecha:** 2026-11-18
**Programa:** `memoria-oral`, paso 8
**Objeto:** timestamps de transcripción y correspondencia hueco → pregunta.

## Veredicto: PASS CON UNA OBSERVACIÓN

## 1. Timestamps contra el audio real

| Medición | Valor | Fuente |
|---|---|---|
| Duración del audio | 7.125750 s | `afinfo data/demo/entrevista-demo.wav` |
| `offsets` del segmento | 0 → 6760 ms | `data/demo/out.json` |
| `timestamps` del segmento | `00:00:00,000` → `00:00:06,760` | idem |
| Consistencia offsets ↔ timestamps | 6760 ms = 00:00:06,760 ✅ | cálculo |

**Observación:** el segmento termina en 6760 ms y el audio dura 7125 ms. Los 365 ms restantes son silencio final, no habla. El timestamp es correcto; no cubre el archivo entero porque no hay texto que cubrir.

**Verificación de la DB:** `data/index.db` tiene `inicio_ms=0`, `fin_ms=6760`, texto completo. Coincide con el JSON.

## 2. Texto transcrito

> "Nací en Bahía Blanca en el 42. Mi papá trabajaba en el ferrocarril y mi mamá cosía para las vecinas."

Se compara contra el texto que se sintetizó con `say -v Paulina`:
> "Nací en Bahía Blanca en el cuarenta y dos. Mi papá trabajaba en el ferrocarril y mi mamá cosía para las vecinas."

Diferencias: **una sola**, "cuarenta y dos" → "42". Es normalización numérica de Whisper, correcta en significado. Nada más se perdió.

## 3. Correspondencia hueco → pregunta

| Elemento | Valor real observado |
|---|---|
| Huecos detectados | `migración`, `recuerdos` |
| Categoría que eligió el agente | `recuerdos` |
| Pregunta | "¿Podrías contarme un recuerdo que tengas de tu infancia en Bahía Blanca?" |
| Motivo declarado | "Aporta un momento concreto de la infancia que enriquece la historia personal" |

**PASS** en el mecanismo: la categoría que devuelve el agente está validada contra el conjunto de huecos (`categoria = data.get("categoria") if data.get("categoria") in categorias else huecos[0]["categoria"]`, `questions.py`).

**Observación:** la pregunta mezcla dos huecos ("recuerdos" declarado, pero pregunta por "infancia", que corresponde a "niñez" — ya cubierto). El mecanismo es correcto; la calidad del texto no. Esto es consistente con la falla de voseo ya reportada.

## 4. Falla de voseo (repetida)

Dos muestras reales, dos fallas:

1. "¿Y qué sentías, **vos**, cuando el tren llegaba...?" — del brief de MIND, correcto.
2. "¿Podrías contarme un recuerdo que **tengas**...?" — de esta corrida, incorrecto (esperado "tengás").

El prompt pide voseo explícitamente. El modelo no lo cumple de forma consistente. **No es un bug del código, es una limitación del modelo de 4B.** Mitigación posible: agregar 2-3 ejemplos de voseo en el prompt del sistema.

## 5. Evidencia reproducible

```bash
cd projects/memoria-oral
PYTHONPATH=src uv run python -m memori.oral.transcribe data/demo/entrevista-demo.wav
PYTHONPATH=src uv run python -c "import json; d=json.load(open('data/demo/out.json')); print(d['transcription'][0]['offsets'])"
afinfo data/demo/entrevista-demo.wav | grep duration
```
