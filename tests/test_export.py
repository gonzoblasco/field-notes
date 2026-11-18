from pathlib import Path

from memori.oral.db import get_huecos, init_db, insert_entrevista, insert_hueco, insert_segmento
from memori.oral.export_md import export_markdown, render_markdown


def _seed(conn):
    eid = insert_entrevista(conn, titulo="Entrevista de prueba", persona="Abuela", consentimiento=1)
    insert_segmento(conn, eid, 0, 5000, "Nací en Bahía Blanca en el 42.")
    insert_segmento(conn, eid, 5000, 9000, "Mi papá trabajaba en el ferrocarril.")
    insert_hueco(conn, eid, "migración", "No contó cómo llegó a Buenos Aires.", 0)
    return eid


def test_render_markdown_contains_sections(tmp_path):
    conn = init_db(tmp_path / "t.db")
    eid = _seed(conn)
    md = render_markdown(conn, eid, {"pregunta": "¿Cómo fue el viaje?", "categoria": "migración", "por_que": "hueco"})
    assert "# Entrevista de prueba" in md
    assert "00:00–00:05" in md
    assert "migración" in md
    assert "¿Cómo fue el viaje?" in md
    conn.close()


def test_export_writes_file(tmp_path):
    conn = init_db(tmp_path / "t.db")
    eid = _seed(conn)
    out = export_markdown(conn, eid, tmp_path / "out" / "entrevista.md")
    assert out.is_file()
    assert "Bahía Blanca" in out.read_text(encoding="utf-8")
    conn.close()
