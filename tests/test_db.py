import os
import tempfile

import pytest

from memori.oral.db import (
    init_db,
    insert_entrevista,
    insert_segmento,
    insert_hueco,
    list_entrevistas,
    get_segmentos,
    get_huecos,
    search_segmentos,
)


@pytest.fixture
def db_conn():
    # create a temporary file for the SQLite DB
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    conn = init_db(path)
    yield conn
    conn.close()
    os.remove(path)


def test_workflow(db_conn):
    # Insert one entrevista
    entrevista_id = insert_entrevista(
        db_conn,
        titulo="Entrevista de prueba",
        audio_path="/tmp/audio.mp3",
        fecha="2026-11-01",
        persona="Juan",
        consentimiento=1,
    )

    # Insert three segmentos
    insert_segmento(db_conn, entrevista_id, 0, 1000, "Hola mundo")
    insert_segmento(db_conn, entrevista_id, 1000, 2000, "Este es un segmento de prueba")
    insert_segmento(db_conn, entrevista_id, 2000, 3000, "Adiós")

    # Insert two huecos
    insert_hueco(db_conn, entrevista_id, "tipo1", "descripcion 1")
    insert_hueco(db_conn, entrevista_id, "tipo2", "descripcion 2", cubierto=1)

    # Verify counts
    assert len(list_entrevistas(db_conn)) == 1
    assert len(get_segmentos(db_conn, entrevista_id)) == 3
    assert len(get_huecos(db_conn, entrevista_id)) == 2

    # Search for a word present in one segment
    hits = search_segmentos(db_conn, "Adiós")
    assert len(hits) == 1
    seg_id, text = hits[0]
    assert "Adiós" in text

