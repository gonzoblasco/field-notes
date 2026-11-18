# Memoria Oral — local oral history

A local-first AI agent that records family interviews, transcribes them on your own machine, finds the gaps in the story, and asks the next question.

No cloud. No API keys. The voices never leave the laptop.

> **This project was built for the [Hacktoberfest 2026 — Week 4: Ghost in the Machine](https://dev.to/challenges/hacktoberfest-week4-2026-10-26) challenge on DEV.to.**
>
> That challenge asked for something spooky, or something that honors the past in the spirit of Día de los Muertos, built with open-source AI at its core. The official deadline was October 31, 2026. This work started after it, so it is **not a submission** — it is a public continuation of the idea. The origin, prompt, and constraints are credited here in full.

---

## The problem

A voice is the one thing in a family archive that cannot be recovered. If it leaks, it cannot be rotated like a password. And the stories that matter most — how someone arrived, what their neighborhood was like, what they regret — are told once, casually, and then lost.

Commercial transcription services solve the text problem and create a privacy problem: your family's voice recordings get processed by subprocessors in another jurisdiction (Otter, for example, [lists AWS US, Anthropic and OpenAI](https://otter.ai/subprocessors)).

Memoria Oral keeps the whole pipeline on the interviewer's machine.

## What it does

1. **Transcribes locally** with `whisper.cpp` and `ggml-large-v3-turbo-q5_0` (~4.4× real time on Apple Silicon, measured).
2. **Stores** interviews and timestamped segments in SQLite with FTS5.
3. **Detects gaps** against a configurable checklist (childhood, family, work, migration, memories).
4. **Asks the next question** with a small local LLM, grounded in the gap it detected.
5. **Exports** the interview to Markdown, readable without the app.

Every AI component is load-bearing:

| Component | Role | Remove it and… |
|---|---|---|
| Whisper (MIT) | Speech → text with timestamps | there is no archive |
| Checklist | Defines what a life story should cover | the questions are generic |
| Qwen3-4B (Apache-2.0) | Turns a gap into a question | the user has to think of it alone |

## Why open models matter here

This is not a cost argument. It is a consent argument.

- **The audio never leaves the machine.** Verified with `lsof`: 0 sockets during transcription (`docs/privacy-check.md`).
- **The model can be swapped.** If a better Spanish model appears, it is a config change, not a migration.
- **Nothing is rented.** The archive still opens in ten years, on a laptop, without a subscription.
- **The pipeline is auditable.** Every claim in `docs/` can be re-run.

## Design principles

Approved before writing code, and enforced in the UI:

1. **Consent before code.** The app explains what is recorded, where it stays, who can listen, and how to delete it. Transcription is blocked without an explicit checkbox.
2. **The person is the author.** The export carries their name. The family does not decide for them.
3. **An agent does not replace a grandchild.** The agent suggests questions. The relationship is human.
4. **No real data in the demo without permission.**

## Stack

| Layer | Choice | Why |
|---|---|---|
| Speech | `whisper.cpp` 1.9.5 + `ggml-large-v3-turbo-q5_0` (547 MB) | MIT, ~4.4× real time measured |
| LLM | Ollama + `qwen3:4b-instruct-2507-q4_K_M` | Apache-2.0, 4.5 s per question measured |
| Store | SQLite + FTS5 | One file, no server |
| UI | FastAPI + Jinja2, one screen, `127.0.0.1` | No Electron, no build step |
| Language | Python 3.11+ | Audio ecosystem |

## Quickstart

```bash
# 1. Requirements
brew install whisper.cpp uv
curl -L -o models/ggml-large-v3-turbo-q5_0.bin \
  https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-large-v3-turbo-q5_0.bin
ollama pull qwen3:4b-instruct-2507-q4_K_M

# 2. Install and run
uv sync
PYTHONPATH=src uv run uvicorn memori.oral.ui:app --port 8100
# open http://127.0.0.1:8100

# 3. Tests
uv run pytest -q      # 8 tests
```

The model file is not in the repo (547 MB). The command above is the only download.

## Evidence

| Claim | Measurement | Where |
|---|---|---|
| Transcription is fast enough | 7.1 s audio → 1.63 s compute (4.4× real time) | `docs/audit-timestamps.md` |
| Timestamps match the audio | segment 0–6760 ms vs `afinfo` 7125 ms (remaining is silence) | idem |
| Transcription is accurate | word-for-word match on the demo, except "cuarenta y dos" → "42" | idem |
| No network during transcription | 9 `lsof` samples, 0 connections | `docs/privacy-check.md` |
| The question targets a real gap | category validated against the gap set | `docs/audit-timestamps.md` §3 |

## Limitations (honest list)

- **Voseo is inconsistent.** The prompt asks for Rioplatense Spanish and gives examples; the 4B model still slips into "tú" forms sometimes. Measured twice wrong, once right. A larger model or a fine-tune would fix it; the project does not claim it is solved.
- **The bundled demo audio is synthetic** (`say -v Paulina`). It proves the pipeline, not the accuracy on real elders, accents, or background noise.
- **Consent is a checkbox, not a signature.** The database stores the flag; it is not a legal instrument.
- **No diarization.** One speaker per file. Two-person interviews are out of scope.
- **Single language per run.** Spanish by default.
- **The UI binds to loopback only.** Running it with `--host 0.0.0.0` would expose the archive to the network; that is deliberately not in the Makefile.

## Repository layout

```
src/memori/oral/
  transcribe.py   whisper.cpp wrapper, WAV conversion, DB insert
  db.py           SQLite schema (entrevistas, segmentos, huecos) + FTS5
  checklist.py    coverage detection against a configured checklist
  questions.py    local LLM that turns a gap into a question
  export_md.py    Markdown export
  ui.py           FastAPI routes
docs/
  audit-timestamps.md   timestamp and citation verification
  privacy-check.md      lsof evidence and ethical framing
.knowledge/
  BRIEF.md        original brief, scope and definition of done
```

## Origin and credits

- **Challenge:** [DEV.to — Hacktoberfest 2026, Week 4: Ghost in the Machine](https://dev.to/challenges/hacktoberfest-week4-2026-10-26). Prompt: *build something spooky, or something that honors the past, with open-source AI at its core.*
- **Feasibility research:** internal brief comparing local STT options, licences, and model sizes. Its findings are summarized in the Evidence and Limitations sections.
- **Models:** [whisper.cpp](https://github.com/ggerganov/whisper.cpp) (MIT) and [Qwen3-4B-Instruct-2507](https://huggingface.co/Qwen/Qwen3-4B-Instruct-2507) (Apache-2.0).
- **Build process:** planned with a step-based planner, implemented by separate role agents (developer, designer, auditor, critic), and every claim in `docs/` was verified against the running code rather than accepted from a self-report.

## License

MIT — see `LICENSE`. Model weights keep their own licenses (Whisper: MIT; Qwen3: Apache-2.0).
