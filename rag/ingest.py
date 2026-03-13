from __future__ import annotations
import time, uuid
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable, List, Optional
import numpy as np

from .chunking import chunk_pages
from .db import get_conn, init_db
from .embeddings import embed_texts
from .extract import extract_text_pages

@dataclass
class IngestResult:
    indexed: int
    skipped: int
    errors: int

def _now() -> str:
    return datetime.utcnow().isoformat()

def _pack(vec: List[float]) -> bytes:
    return np.asarray(vec, dtype=np.float32).tobytes()

def ingest_file(*, db_path: Path, file_id: str, rel_path: str, abs_path: Path,
                openai_api_key: Optional[str], allow_ocr: bool=False) -> None:
    init_db(db_path)
    conn = get_conn(db_path)
    cur = conn.cursor()

    mtime = int(abs_path.stat().st_mtime)
    cur.execute("SELECT mtime FROM rag_files WHERE file_id=?", (file_id,))
    row = cur.fetchone()
    if row and int(row["mtime"]) == mtime:
        conn.close()
        return

    cur.execute("""
    INSERT INTO rag_files(file_id, rel_path, mtime, indexed_at, status, error)
    VALUES(?, ?, ?, ?, 'indexing', NULL)
    ON CONFLICT(file_id) DO UPDATE SET
        rel_path=excluded.rel_path,
        mtime=excluded.mtime,
        indexed_at=excluded.indexed_at,
        status='indexing',
        error=NULL
    """, (file_id, rel_path, mtime, _now()))
    cur.execute("DELETE FROM rag_chunks WHERE file_id=?", (file_id,))
    conn.commit()

    try:
        pages, is_scanned = extract_text_pages(abs_path)

        if is_scanned and allow_ocr and abs_path.suffix.lower() == ".pdf":
            from .ocr import ocr_pdf_to_pages
            pages = ocr_pdf_to_pages(abs_path)

        chunks = [c for c in chunk_pages(pages) if len(c.text.strip()) >= 30]
        if not chunks:
            cur.execute("UPDATE rag_files SET indexed_at=?, status=?, error=? WHERE file_id=?",
                        (_now(), "empty", "No extractable text", file_id))
            conn.commit()
            conn.close()
            return

        BATCH = 64
        for start in range(0, len(chunks), BATCH):
            batch = chunks[start:start+BATCH]
            vectors = embed_texts([c.text for c in batch], api_key=openai_api_key)
            for c, v in zip(batch, vectors):
                cur.execute("""
                INSERT INTO rag_chunks(id, file_id, rel_path, page, chunk_index, text, embedding, dim, updated_at)
                VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (str(uuid.uuid4()), file_id, rel_path, c.page, int(c.chunk_index), c.text,
                      _pack(v), int(len(v)), _now()))
            conn.commit()

        cur.execute("UPDATE rag_files SET indexed_at=?, status=?, error=NULL WHERE file_id=?",
                    (_now(), "ok", file_id))
        conn.commit()
    except Exception as e:
        cur.execute("UPDATE rag_files SET indexed_at=?, status=?, error=? WHERE file_id=?",
                    (_now(), "error", f"{type(e).__name__}: {e}", file_id))
        conn.commit()
        raise
    finally:
        conn.close()

def ingest_all(*, db_path: Path, files: Iterable[tuple[str,str,Path]], openai_api_key: Optional[str],
              allow_ocr: bool=False, max_seconds: Optional[int]=None) -> IngestResult:
    init_db(db_path)
    started = time.time()
    res = IngestResult(indexed=0, skipped=0, errors=0)
    for file_id, rel_path, abs_path in files:
        if max_seconds and (time.time() - started) > max_seconds:
            break
        try:
            before = time.time()
            ingest_file(db_path=db_path, file_id=file_id, rel_path=rel_path, abs_path=abs_path,
                        openai_api_key=openai_api_key, allow_ocr=allow_ocr)
            if (time.time() - before) < 0.02:
                res.skipped += 1
            else:
                res.indexed += 1
        except Exception:
            res.errors += 1
    return res
