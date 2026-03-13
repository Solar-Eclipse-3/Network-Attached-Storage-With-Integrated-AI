from __future__ import annotations

import json
import mimetypes
import re
import uuid
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Iterable, List, Optional

from werkzeug.datastructures import FileStorage

TEXT_EXTENSIONS = {".txt", ".md", ".csv", ".json", ".log"}
DOC_EXTENSIONS = {".doc", ".docx"}
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp"}
VIDEO_EXTENSIONS = {".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm"}
ALLOWED_EXTENSIONS = (
    TEXT_EXTENSIONS
    | DOC_EXTENSIONS
    | IMAGE_EXTENSIONS
    | VIDEO_EXTENSIONS
    | {".pdf"}
)

# Max upload size in bytes (100 MB)
MAX_UPLOAD_SIZE = 100 * 1024 * 1024


def _tokenize(text: str) -> List[str]:
    return [w for w in re.findall(r"[A-Za-z0-9]+", text.lower()) if len(w) > 2]


def _read_text_snippet(path: Path, extension: str, limit: int = 4000) -> str:
    try:
        if extension in TEXT_EXTENSIONS:
            return path.read_text(errors="ignore")[:limit]
        if extension == ".pdf":
            try:
                from PyPDF2 import PdfReader  # type: ignore
            except Exception:
                return ""

            reader = PdfReader(str(path))
            buffer = []
            for page in reader.pages:
                if len("".join(buffer)) > limit:
                    break
                buffer.append(page.extract_text() or "")
            return "".join(buffer)[:limit]
        if extension in DOC_EXTENSIONS:
            try:
                import docx2txt  # type: ignore
            except Exception:
                return ""

            return (docx2txt.process(str(path)) or "")[:limit]
    except Exception:
        return ""
    return ""


def _derive_type(extension: str) -> str:
    if extension in IMAGE_EXTENSIONS:
        return "image"
    if extension in VIDEO_EXTENSIONS:
        return "video"
    if extension == ".pdf":
        return "pdf"
    if extension in TEXT_EXTENSIONS:
        return "txt"
    if extension in DOC_EXTENSIONS:
        return "doc"
    return "other"


def _derive_category(file_type: str) -> str:
    if file_type == "image":
        return "Pictures"
    if file_type == "video":
        return "Videos"
    if file_type in {"pdf", "txt", "doc"}:
        return "Documents"
    return "Other"


def _build_keywords(original_name: str, text_snippet: str) -> List[str]:
    tokens = _tokenize(original_name)
    if text_snippet:
        tokens += _tokenize(text_snippet)
    # preserve order but deduplicate
    seen = set()
    deduped = []
    for token in tokens:
        if token not in seen:
            seen.add(token)
            deduped.append(token)
        if len(deduped) >= 80:
            break
    return deduped


@dataclass
class FileEntry:
    id: str
    original_name: str
    stored_name: str
    relative_path: str
    extension: str
    mime_type: str
    size: int
    uploaded_at: str
    type: str
    category: str
    keywords: List[str]
    text_preview: str
    albums: List[str]

    def score(self, query_tokens: List[str]) -> int:
        if not query_tokens:
            return 0
        name = self.original_name.lower()
        text = self.text_preview.lower()
        keyword_set = set(self.keywords)
        score = 0
        for token in query_tokens:
            if token in keyword_set:
                score += 4
            if token in name:
                score += 3
            occurrences = text.count(token)
            if occurrences:
                score += min(occurrences, 5)
        return score

    def to_public_dict(self) -> dict:
        raw_path = f"/files/{self.id}/raw"
        return {
            "id": self.id,
            "name": self.original_name,
            "stored_name": self.stored_name,
            "relative_path": self.relative_path,
            "extension": self.extension,
            "mime_type": self.mime_type,
            "size": self.size,
            "uploaded_at": self.uploaded_at,
            "type": self.type,
            "category": self.category,
            "keywords": self.keywords,
            "text_preview": self.text_preview,
            "albums": self.albums,
            "download_path": raw_path,
        }


class FileIndex:
    def __init__(self, storage_path: Path):
        self.storage_path = storage_path
        self.upload_dir = storage_path / "uploads"
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.index_file = storage_path / "file_index.json"
        self.albums_file = storage_path / "albums.json"
        self.files: List[FileEntry] = []
        self.albums: List[dict] = []
        self._load_state()
        self.sync_with_disk()

    def _load_state(self):
        if self.index_file.exists():
            try:
                data = json.loads(self.index_file.read_text())
                self.files = [FileEntry(**item) for item in data]
            except Exception:
                self.files = []
        if self.albums_file.exists():
            try:
                self.albums = json.loads(self.albums_file.read_text())
            except Exception:
                self.albums = []

    def _save_files(self):
        data = [asdict(entry) for entry in self.files]
        self.index_file.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def _save_albums(self):
        self.albums_file.write_text(json.dumps(self.albums, indent=2), encoding="utf-8")

    def _iter_allowed_files(self) -> Iterable[Path]:
        for path in self.storage_path.rglob("*"):
            if not path.is_file():
                continue
            if path.name in {"file_index.json", "albums.json"}:
                continue
            ext = path.suffix.lower()
            if ext and ext in ALLOWED_EXTENSIONS:
                yield path

    def sync_with_disk(self):
        existing = {entry.relative_path: entry for entry in self.files}
        refreshed: List[FileEntry] = []
        seen = set()
        for path in self._iter_allowed_files():
            rel = str(path.relative_to(self.storage_path))
            seen.add(rel)
            entry = existing.get(rel)
            if entry:
                entry.size = path.stat().st_size
                if not entry.keywords:
                    entry.keywords = _build_keywords(entry.original_name, entry.text_preview)
                refreshed.append(entry)
                continue
            refreshed.append(self._build_entry(path))

        removed = {rel for rel in existing if rel not in seen}
        if removed or len(refreshed) != len(self.files):
            self.files = refreshed
            self._save_files()

    def _build_entry(self, path: Path, original_name: Optional[str] = None) -> FileEntry:
        extension = path.suffix.lower()
        mime_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        file_type = _derive_type(extension)
        category = _derive_category(file_type)
        snippet = _read_text_snippet(path, extension)
        entry = FileEntry(
            id=str(uuid.uuid4()),
            original_name=original_name or path.name,
            stored_name=path.name,
            relative_path=str(path.relative_to(self.storage_path)),
            extension=extension,
            mime_type=mime_type,
            size=path.stat().st_size,
            uploaded_at=datetime.utcnow().isoformat(),
            type=file_type,
            category=category,
            keywords=_build_keywords(original_name or path.name, snippet),
            text_preview=snippet,
            albums=[],
        )
        return entry

    def add_file(self, file: FileStorage) -> FileEntry:
        ext = Path(file.filename or "").suffix.lower()
        if not ext or ext not in ALLOWED_EXTENSIONS:
            raise ValueError(f"Unsupported file type: {ext or 'unknown'}")

        stored_name = f"{uuid.uuid4().hex}{ext}"
        save_path = self.upload_dir / stored_name
        file.save(save_path)
        # enforce size limit after saving (Flask may stream large files)
        try:
            size = save_path.stat().st_size
            if size > MAX_UPLOAD_SIZE:
                # remove the saved file and reject
                try:
                    save_path.unlink(missing_ok=True)
                except Exception:
                    pass
                raise ValueError("File exceeds maximum allowed size (100 MB)")
        except OSError:
            # unable to stat file, conservatively reject
            try:
                save_path.unlink(missing_ok=True)
            except Exception:
                pass
            raise ValueError("Failed to save uploaded file")
        entry = self._build_entry(save_path, original_name=file.filename or stored_name)
        entry.stored_name = stored_name
        entry.relative_path = str(save_path.relative_to(self.storage_path))
        self.files.append(entry)
        self._save_files()
        return entry

    def list_files(self) -> List[FileEntry]:
        return sorted(self.files, key=lambda f: f.uploaded_at, reverse=True)

    def get_file(self, file_id: str) -> Optional[FileEntry]:
        return next((f for f in self.files if f.id == file_id), None)

    def delete_file(self, file_id: str) -> bool:
        entry = self.get_file(file_id)
        if not entry:
            return False
        try:
            (self.storage_path / entry.relative_path).unlink(missing_ok=True)
        except Exception:
            pass
        self.files = [f for f in self.files if f.id != file_id]
        self._save_files()
        return True

    def search(self, query: str, *, category: Optional[str] = None, limit: int = 12) -> List[FileEntry]:
        tokens = _tokenize(query)
        if not tokens:
            return []
        matches: List[tuple[int, FileEntry]] = []
        for entry in self.files:
            if category and entry.category.lower() != category.lower():
                continue
            score = entry.score(tokens)
            if score > 0:
                matches.append((score, entry))
        matches.sort(key=lambda pair: (pair[0], pair[1].uploaded_at), reverse=True)
        return [entry for _, entry in matches[:limit]]

    def create_album(self, name: str, file_ids: List[str], query: str) -> dict:
        album_id = str(uuid.uuid4())
        album = {
            "id": album_id,
            "name": name,
            "file_ids": file_ids,
            "query": query,
            "created_at": datetime.utcnow().isoformat(),
        }
        self.albums.append(album)
        for entry in self.files:
            if entry.id in file_ids and album_id not in entry.albums:
                entry.albums.append(album_id)
        self._save_albums()
        self._save_files()
        return album

    def list_albums(self) -> List[dict]:
        return sorted(self.albums, key=lambda a: a["created_at"], reverse=True)


def tokenize_text(text: str) -> List[str]:
    return _tokenize(text)
