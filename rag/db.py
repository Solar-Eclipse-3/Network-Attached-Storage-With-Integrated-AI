from __future__ import annotations
import sqlite3
from pathlib import Path

def get_conn(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def init_db(db_path: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = get_conn(db_path)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS rag_chunks (
        id TEXT PRIMARY KEY,
        file_id TEXT NOT NULL,
        rel_path TEXT NOT NULL,
        page INTEGER,
        chunk_index INTEGER NOT NULL,
        text TEXT NOT NULL,
        embedding BLOB,
        dim INTEGER,
        updated_at TEXT NOT NULL
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS rag_files (
        file_id TEXT PRIMARY KEY,
        rel_path TEXT NOT NULL,
        mtime INTEGER NOT NULL,
        indexed_at TEXT NOT NULL,
        status TEXT NOT NULL,
        error TEXT
    )
    """)

    cur.execute("CREATE INDEX IF NOT EXISTS idx_rag_chunks_file ON rag_chunks(file_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_rag_chunks_path ON rag_chunks(rel_path)")
    conn.commit()
    conn.close()
