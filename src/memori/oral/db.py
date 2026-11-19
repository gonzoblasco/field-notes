"""Database layer for Field Notes using SQLite with FTS5.

The schema includes three main tables:

* ``entrevistas`` – basic metadata about each interview.
* ``segmentos`` – textual segments linked to an interview.
* ``huecos`` – gaps or missing pieces associated with an interview.

Additionally an FTS5 virtual table ``segmentos_fts`` is created over the
``texto`` column of ``segmentos`` to enable full‑text search.

All helper functions receive a ``sqlite3.Connection`` object.  The ``init_db``
function creates the database file (if it does not exist) and builds the
schema.  The module purposefully avoids any ORM – a lightweight wrapper
around the standard library keeps the dependency footprint minimal.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Iterable, List, Tuple, Any

# ---------------------------------------------------------------------------
# Schema creation
# ---------------------------------------------------------------------------

def init_db(path: str | Path) -> sqlite3.Connection:
    """Create (or open) a SQLite database with the required schema.

    Parameters
    ----------
    path:
        Destination file for the SQLite database.  Parent directories are
        created automatically.

    Returns
    -------
    sqlite3.Connection
        An open connection with ``row_factory`` set to ``sqlite3.Row`` for
        convenient column access.
    """
    db_path = Path(path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    _create_schema(conn)
    return conn


def _create_schema(conn: sqlite3.Connection) -> None:
    """Create tables and FTS5 virtual table if they do not exist."""
    cur = conn.cursor()
    # Regular tables
    cur.executescript(
        """
        CREATE TABLE IF NOT EXISTS entrevistas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            audio_path TEXT,
            fecha TEXT,
            persona TEXT,
            consentimiento INTEGER
        );

        CREATE TABLE IF NOT EXISTS segmentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entrevista_id INTEGER NOT NULL REFERENCES entrevistas(id) ON DELETE CASCADE,
            inicio_ms INTEGER NOT NULL,
            fin_ms INTEGER NOT NULL,
            texto TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS huecos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entrevista_id INTEGER NOT NULL REFERENCES entrevistas(id) ON DELETE CASCADE,
            categoria TEXT NOT NULL,
            descripcion TEXT NOT NULL,
            cubierto INTEGER NOT NULL DEFAULT 0
        );
        """
    )

    # FTS5 virtual table – content='segmentos' links it to the real table
    cur.execute(
        """
        CREATE VIRTUAL TABLE IF NOT EXISTS segmentos_fts USING fts5(
            texto, content='segmentos', content_rowid='id'
        );
        """
    )

    # Keep the FTS index in sync with inserts via triggers
    cur.executescript(
        """
        CREATE TRIGGER IF NOT EXISTS segmentos_ai AFTER INSERT ON segmentos BEGIN
            INSERT INTO segmentos_fts(rowid, texto) VALUES (new.id, new.texto);
        END;

        CREATE TRIGGER IF NOT EXISTS segmentos_au AFTER UPDATE ON segmentos BEGIN
            INSERT INTO segmentos_fts(segmentos_fts, rowid, texto) VALUES('delete', old.id, old.texto);
            INSERT INTO segmentos_fts(rowid, texto) VALUES (new.id, new.texto);
        END;

        CREATE TRIGGER IF NOT EXISTS segmentos_ad AFTER DELETE ON segmentos BEGIN
            INSERT INTO segmentos_fts(segmentos_fts, rowid, texto) VALUES('delete', old.id, old.texto);
        END;
        """
    )
    conn.commit()


# ---------------------------------------------------------------------------
# CRUD helpers
# ---------------------------------------------------------------------------

def insert_entrevista(
    conn: sqlite3.Connection,
    titulo: str,
    audio_path: str | None = None,
    fecha: str | None = None,
    persona: str | None = None,
    consentimiento: int | None = None,
) -> int:
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO entrevistas (titulo, audio_path, fecha, persona, consentimiento)
        VALUES (?, ?, ?, ?, ?)
        """,
        (titulo, audio_path, fecha, persona, consentimiento),
    )
    conn.commit()
    return cur.lastrowid


def insert_segmento(
    conn: sqlite3.Connection,
    entrevista_id: int,
    inicio_ms: int,
    fin_ms: int,
    texto: str,
) -> int:
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO segmentos (entrevista_id, inicio_ms, fin_ms, texto)
        VALUES (?, ?, ?, ?)
        """,
        (entrevista_id, inicio_ms, fin_ms, texto),
    )
    conn.commit()
    return cur.lastrowid


def insert_hueco(
    conn: sqlite3.Connection,
    entrevista_id: int,
    categoria: str,
    descripcion: str,
    cubierto: int = 0,
) -> int:
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO huecos (entrevista_id, categoria, descripcion, cubierto)
        VALUES (?, ?, ?, ?)
        """,
        (entrevista_id, categoria, descripcion, cubierto),
    )
    conn.commit()
    return cur.lastrowid


def list_entrevistas(conn: sqlite3.Connection) -> List[sqlite3.Row]:
    cur = conn.cursor()
    cur.execute("SELECT * FROM entrevistas ORDER BY id")
    return cur.fetchall()


def get_segmentos(conn: sqlite3.Connection, entrevista_id: int) -> List[sqlite3.Row]:
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM segmentos WHERE entrevista_id = ? ORDER BY inicio_ms",
        (entrevista_id,),
    )
    return cur.fetchall()


def get_huecos(conn: sqlite3.Connection, entrevista_id: int) -> List[sqlite3.Row]:
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM huecos WHERE entrevista_id = ? ORDER BY id",
        (entrevista_id,),
    )
    return cur.fetchall()


def search_segmentos(conn: sqlite3.Connection, query: str) -> List[Tuple[int, str]]:
    """Full‑text search over ``segmentos.texto``.

    Returns a list of ``(segmento_id, texto)`` tuples ordered by relevance.
    """
    cur = conn.cursor()
    cur.execute(
        "SELECT rowid, texto FROM segmentos_fts WHERE segmentos_fts MATCH ?",
        (query,),
    )
    return [(row[0], row[1]) for row in cur.fetchall()]

