from __future__ import annotations
from pathlib import Path
from typing import List, Tuple

def extract_text_pages(path: Path) -> Tuple[List[str], bool]:
    ext = path.suffix.lower()

    if ext == ".pdf":
        try:
            from PyPDF2 import PdfReader
        except Exception:
            return ([], False)

        reader = PdfReader(str(path))
        pages: List[str] = []
        total_chars = 0
        for p in reader.pages:
            text = (p.extract_text() or "").strip()
            pages.append(text)
            total_chars += len(text)
        is_scanned = total_chars < 50
        return (pages, is_scanned)

    try:
        text = path.read_text(errors="ignore")
        return ([text], False)
    except Exception:
        return ([], False)
