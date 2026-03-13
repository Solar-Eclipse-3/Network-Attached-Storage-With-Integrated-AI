from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple
import numpy as np

from .db import get_conn, init_db
from .embeddings import embed_texts

@dataclass
class RetrievedChunk:
    rel_path: str
    file_id: str
    page: Optional[int]
    chunk_index: int
    text: str
    score: float

def _unpack(blob: bytes, dim: int) -> np.ndarray:
    return np.frombuffer(blob, dtype=np.float32)

def _cosine(a: np.ndarray, b: np.ndarray) -> float:
    denom = (np.linalg.norm(a) * np.linalg.norm(b))
    return 0.0 if denom == 0 else float(np.dot(a, b) / denom)

def retrieve(*, db_path: Path, query: str, openai_api_key: Optional[str], top_k: int=6, max_candidates: int=5000) -> List[RetrievedChunk]:
    init_db(db_path)
    q_vec = embed_texts([query], api_key=openai_api_key)[0]
    q = np.asarray(q_vec, dtype=np.float32)

    conn = get_conn(db_path)
    cur = conn.cursor()
    cur.execute("""
    SELECT rel_path, file_id, page, chunk_index, text, embedding, dim
    FROM rag_chunks
    WHERE embedding IS NOT NULL
    ORDER BY updated_at DESC
    LIMIT ?
    """, (max_candidates,))
    rows = cur.fetchall()
    conn.close()

    scored: List[RetrievedChunk] = []
    for r in rows:
        v = _unpack(r["embedding"], int(r["dim"] or 0))
        s = _cosine(q, v)
        scored.append(RetrievedChunk(
            rel_path=r["rel_path"], file_id=r["file_id"],
            page=int(r["page"]) if r["page"] is not None else None,
            chunk_index=int(r["chunk_index"]), text=r["text"], score=s
        ))

    scored.sort(key=lambda c: c.score, reverse=True)
    return scored[:top_k]

def format_context(chunks: List[RetrievedChunk], *, max_chars: int=4500) -> Tuple[str, List[dict]]:
    context_parts: List[str] = []
    citations: List[dict] = []
    used = 0
    for c in chunks:
        cite = {"path": c.rel_path, "page": c.page, "chunk": c.chunk_index, "score": round(c.score, 4)}
        block = f"SOURCE: {c.rel_path} | page {c.page or '?'} | chunk {c.chunk_index}\n{c.text.strip()}"
        if used + len(block) > max_chars:
            break
        context_parts.append(block)
        citations.append(cite)
        used += len(block)
    return "\n\n---\n\n".join(context_parts), citations
