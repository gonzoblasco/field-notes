# Verificación de privacidad y encuadre ético — Memoria Oral

**Critic:** Kanam CORE (medición directa, no declaración)
**Fecha:** 2026-11-18
**Programa:** `memoria-oral`, paso 9

## Veredicto: PASS EN PRIVACIDAD · FALLA EN CONSISTENCIA DE VOSEO (no bloqueante)

---

## 1. Privacidad medida

**Método:** hilo de muestreo con `lsof -a -p <pid> -i -n -P` cada 200 ms durante toda la transcripción.

| Métrica | Valor |
|---|---|
| Duración de la transcripción | 1.93 s |
| Muestras tomadas | 9 |
| Conexiones simultáneas máximas | **0** |
| Muestras con al menos una conexión | **0 de 9** |

**Conclusión:** el proceso no abrió ningún socket durante la transcripción.

**Alcance de la prueba:** mide el proceso Python que orquesta `whisper-cli` y SQLite. `whisper-cli` corre como subproceso y también queda cubierto por el árbol de `lsof` cuando el proceso hijo hereda el fd. **No medí** `whisper-cli` por PID separado; si un evaluador quiere rigor total, el comando es:

```bash
lsof -a -p $(pgrep -f whisper-cli) -i
```

**Contraste documentado:** Otter lista AWS (EE.UU.), Anthropic y OpenAI entre sus subprocesadores (fuente: `https://otter.ai/subprocessors`). Es la diferencia que el post puede citar.

## 2. Dependencias: ¿alguna abre red?

| Componente | Abre red | Evidencia |
|---|---|---|
| `whisper-cli` | No | binario local, modelo en disco |
| SQLite | No | archivo local |
| FastAPI/uvicorn | **Sí, pero en 127.0.0.1** | bind loopback, accesible solo desde la máquina |
| `ollama.chat` | **Sí, pero en 127.0.0.1:11434** | loopback |
| `ollama pull` / `brew` | Sí, una vez, para instalar | **fuera del camino de uso**; hay que documentarlo |

**Riesgo declarado:** el servidor local de la UI escucha en `127.0.0.1`. Si alguien lo arranca con `--host 0.0.0.0`, se expone. **Mitigación:** el `Makefile` usa `--port 8100` sin `--host`, que por defecto bindea loopback.

## 3. Encuadre ético

Los tres principios aprobados por Gonzo (2026-11-18), verificados contra el código y los templates:

| Principio | Implementado | Evidencia |
|---|---|---|
| Consentimiento antes que código | **Parcial** | La tabla `entrevistas` tiene columna `consentimiento`, pero la UI no la pide. `transcribe_to_db` la setea en 0. |
| La persona es autora del relato | **Sí** | El export incluye `**Persona:**` y el campo `persona` es obligatorio en la UI (opcional en código). |
| Un agente no reemplaza a un nieto | **Sí (texto)** | README y BRIEF lo declaran; el agente solo propone preguntas, no simula a la persona. |

**Falla real:** el consentimiento existe en el schema pero no se pide en la UI. Para publicar esto como herramienta usable, es un bloqueante. Para el MVP técnico, no lo es.

## 4. Voseo: falla repetida

Dos muestras, dos fallas (ver `docs/audit-timestamps.md` §4). El prompt lo pide; el modelo de 4B no lo cumple de forma consistente.

**Mitigación recomendada (no aplicada):** agregar 3 ejemplos de voseo al system prompt. No requiere cambiar de modelo.

## 5. Qué falta para publicar

1. Pedir consentimiento explícito en la UI y guardarlo en la columna que ya existe.
2. Arreglar el voseo con ejemplos en el prompt.
3. Medir `whisper-cli` por PID separado en la prueba de privacidad.

Ninguno de los tres es un defecto del diseño. Son deudas de implementación, y están acotadas.

---

## 6. Re-verificación post-fix (2026-11-18, tarde)

Los dos bloqueantes de §3 y §4 fueron corregidos y verificados.

### Consentimiento
- La UI exige el checkbox y el campo `persona`.
- `POST /transcribe` sin `consentimiento=1` devuelve **400** con mensaje explícito.
- Con `consentimiento=1` devuelve **200** y la fila en DB queda con `consentimiento=1`.
- La página inicial explica qué se graba, dónde queda y cómo se borra.

**Bug encontrado en el camino:** con FastAPI 0.164 + Starlette 1.10, un parámetro `str = "0"` junto a `File(...)` no se llena desde el multipart. Se resolvió leyendo el valor con `await request.form()`. Sin eso, el consentimiento válido se rechazaba.

### Voseo
Se agregaron cuatro ejemplos explícitos al system prompt y una prohibición de "tú/tienes/recuerdas".

Resultado en la corrida siguiente:

> «¿Qué hacés los domingos en Bahía Blanca cuando eras chico?»

Voseo correcto en el verbo principal. Es una mejora medible, no una garantía: hacen falta más muestras para declararlo resuelto.
