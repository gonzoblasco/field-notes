"""Demo script for the memoria‑oral SQLite store.

Running the module creates a ``data/index.db`` file populated with synthetic
data (one interview, three segments and two gaps) and prints basic counts.
"""

from pathlib import Path

from memori.oral.db import (
    init_db,
    insert_entrevista,
    insert_segmento,
    insert_hueco,
    list_entrevistas,
    get_segmentos,
    get_huecos,
)


def main() -> None:
    db_path = Path(__file__).parents[2] / "data" / "index.db"
    # Use real transcription if the demo audio file exists, otherwise fall back
    # to synthetic data as before.
    audio_demo = Path(__file__).parents[2] / "data" / "demo" / "entrevista-demo.wav"
    if audio_demo.is_file():
        from memori.oral.transcribe import transcribe_to_db

        # Ensure a fresh DB for the demo.
        conn = init_db(db_path)
        conn.close()
        transcribe_to_db(
            audio_path=audio_demo,
            db_path=db_path,
            model_path=Path(__file__).parents[2] / "models" / "ggml-large-v3-turbo-q5_0.bin",
            titulo="Demo entrevista",
            persona="Demo Persona",
        )
        conn = init_db(db_path)  # reopen to query
        # Get the interview we just inserted.
        cur = conn.cursor()
        cur.execute("SELECT id FROM entrevistas WHERE titulo = ?", ("Demo entrevista",))
        entrevista_id = cur.fetchone()["id"]
    else:
        conn = init_db(db_path)
        entrevista_id = insert_entrevista(
            conn,
            titulo="Demo entrevista",
            audio_path=str(db_path.parent / "demo_audio.mp3"),
            fecha="2026-11-18",
            persona="Demo Persona",
            consentimiento=1,
        )

        # three synthetic segments
        insert_segmento(conn, entrevista_id, 0, 1000, "Primer segmento de ejemplo")
        insert_segmento(conn, entrevista_id, 1000, 2000, "Segundo segmento con más texto")
        insert_segmento(conn, entrevista_id, 2000, 3000, "Tercer segmento final")

        # two synthetic huecos
        insert_hueco(conn, entrevista_id, "gap", "primer hueco")
        insert_hueco(conn, entrevista_id, "gap", "segundo hueco", cubierto=1)

    # Print counts
    entrevistas = list_entrevistas(conn)
    print(f"Entrevistas: {len(entrevistas)}")
    print(f"Segmentos: {len(get_segmentos(conn, entrevista_id))}")
    print(f"Huecos: {len(get_huecos(conn, entrevista_id))}")


if __name__ == "__main__":
    main()

