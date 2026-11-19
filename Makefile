.PHONY: install run demo test lint

install:
	uv sync

run:
	PYTHONPATH=src uv run python -m memori.oral.serve

demo:
	uv run python -m memori.oral.demo

# Run the demo transcription on the bundled audio using the real whisper model.
demo-transcribe:
	@echo "Running demo transcription..."
	uv run python -m memori.oral.transcribe \
		data/demo/entrevista-demo.wav \
		data/demo/index.db \
		models/ggml-large-v3-turbo-q5_0.bin \
		"Demo entrevista"

test:
	uv run pytest -q

lint:
	uv run ruff check src tests
