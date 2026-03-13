from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable, List, Optional

@dataclass
class TextChunk:
    text: str
    page: Optional[int]
    chunk_index: int

def chunk_text(text: str, *, max_chars: int = 2500, overlap_chars: int = 300, page: Optional[int]=None) -> List[TextChunk]:
    text = (text or "").strip()
    if not text:
        return []
    chunks: List[TextChunk] = []
    i = 0
    idx = 0
    n = len(text)
    while i < n:
        j = min(i + max_chars, n)
        chunk = text[i:j].strip()
        if chunk:
            chunks.append(TextChunk(text=chunk, page=page, chunk_index=idx))
            idx += 1
        if j >= n:
            break
        i = max(0, j - overlap_chars)
    return chunks

def chunk_pages(pages: Iterable[str], *, max_chars: int = 2500, overlap_chars: int = 300) -> List[TextChunk]:
    out: List[TextChunk] = []
    global_idx = 0
    for page_i, page_text in enumerate(pages, start=1):
        for c in chunk_text(page_text, max_chars=max_chars, overlap_chars=overlap_chars, page=page_i):
            c.chunk_index = global_idx
            out.append(c)
            global_idx += 1
    return out
