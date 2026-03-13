from __future__ import annotations
from pathlib import Path
from typing import List
import shutil

def ocr_pdf_to_pages(path: Path, *, dpi: int=250, lang: str="eng") -> List[str]:
    """
    OCR a PDF to extract text from scanned images.
    
    Requirements:
    - Python: pip install pytesseract pdf2image pillow
    - System: brew install tesseract poppler
    
    If system tools are missing, raises RuntimeError with installation instructions.
    """
    try:
        from pdf2image import convert_from_path
        import pytesseract
    except Exception as e:
        raise RuntimeError(
            "OCR Python packages missing. Install: pip install pytesseract pdf2image pillow"
        ) from e
    
    # Check system dependencies
    if not shutil.which("tesseract"):
        raise RuntimeError(
            "OCR is enabled but tesseract is not installed.\n"
            "Install with: brew install tesseract poppler\n"
            "Or disable OCR by setting RAG_OCR=0 in .env"
        )
    
    if not shutil.which("pdftoppm"):
        raise RuntimeError(
            "OCR is enabled but poppler is not installed.\n"
            "Install with: brew install tesseract poppler\n"
            "Or disable OCR by setting RAG_OCR=0 in .env"
        )

    images = convert_from_path(str(path), dpi=dpi)
    return [(pytesseract.image_to_string(img, lang=lang) or "").strip() for img in images]
