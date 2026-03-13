from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from dotenv import load_dotenv
from pathlib import Path
import os
from openai import OpenAI
import traceback
import sqlite3
import uuid
import mimetypes
from datetime import datetime
import re

from file_index import FileIndex, tokenize_text, MAX_UPLOAD_SIZE
from image_classifier import classify_any, classify_image, classify_pet

# RAG (kept separate from FileWizardAI/*)
try:
    from rag.ingest import ingest_all
    from rag.retrieve import retrieve, format_context
except Exception:
    ingest_all = None
    retrieve = None
    format_context = None

load_dotenv()

app = Flask(__name__)
CORS(app)

# Config
STORAGE_PATH = Path("storage")
STORAGE_PATH.mkdir(exist_ok=True)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") or os.getenv("API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL") or "gpt-3.5-turbo"

UPLOAD_API_KEY = os.getenv("UPLOAD_API_KEY")  # Optional: require X-API-KEY header for uploads

# Ensure storage subdirs
FILES_DIR = STORAGE_PATH / "files"
FILES_DIR.mkdir(parents=True, exist_ok=True)

# Simple SQLite index
DATA_DIR = Path("data")
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DATA_DIR / "files.db"

# RAG configuration
RAG_ENABLED = (os.getenv("RAG_ENABLED") or "0") in {"1","true","True","yes","YES"}
RAG_ALLOW_OCR = (os.getenv("RAG_OCR") or "0") in {"1","true","True","yes","YES"}
RAG_DB_PATH = DATA_DIR / "rag.db"
RAG_MIN_SCORE = float(os.getenv("RAG_MIN_SCORE") or "0.25")  # Minimum cosine similarity threshold


def get_db_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute(
        """
    CREATE TABLE IF NOT EXISTS files (
        id TEXT PRIMARY KEY,
        filename TEXT,
        path TEXT,
        mime TEXT,
        size INTEGER,
        uploaded_at TEXT,
        text TEXT,
        tags TEXT
    )
    """
    )
    cur.execute(
        """
    CREATE TABLE IF NOT EXISTS albums (
        id TEXT PRIMARY KEY,
        name TEXT,
        created_at TEXT
    )
    """
    )
    cur.execute(
        """
    CREATE TABLE IF NOT EXISTS album_files (
        album_id TEXT,
        file_id TEXT,
        PRIMARY KEY (album_id, file_id)
    )
    """
    )
    
    # Migration: Add tags column if it doesn't exist
    try:
        cur.execute("SELECT tags FROM files LIMIT 1")
    except sqlite3.OperationalError:
        cur.execute("ALTER TABLE files ADD COLUMN tags TEXT")
        print("✅ Added tags column to files table")
    
    conn.commit()
    conn.close()


init_db()

# File/album index
file_index = FileIndex(STORAGE_PATH)

# RAG helper functions
def _iter_rag_docs():
    """Iterate over documents suitable for RAG indexing"""
    for e in file_index.list_files():
        if e.category != "Documents":
            continue
        if e.extension.lower() not in {".pdf",".txt",".md",".csv",".json",".log"}:
            continue
        p = STORAGE_PATH / e.relative_path
        if p.exists():
            yield (e.id, e.relative_path, p)

def rag_reindex_quick(max_seconds: int = 3):
    """Quick incremental RAG index on startup (skips already-indexed files)"""
    if not RAG_ENABLED or ingest_all is None:
        return None
    try:
        return ingest_all(
            db_path=RAG_DB_PATH,
            files=_iter_rag_docs(),
            openai_api_key=OPENAI_API_KEY,
            allow_ocr=RAG_ALLOW_OCR,
            max_seconds=max_seconds,
        )
    except Exception:
        return None

# Initialize OpenAI client if API key is configured
client = None
if OPENAI_API_KEY:
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
    except Exception as e:
        print("Error initializing OpenAI client:", repr(e))
        client = None

# Run quick RAG indexing on startup (incremental, max 3 seconds)
if RAG_ENABLED:
    print("RAG enabled - running quick index...")
    rag_result = rag_reindex_quick(max_seconds=3)
    if rag_result:
        print(f"RAG indexed: {rag_result.indexed}, skipped: {rag_result.skipped}, errors: {rag_result.errors}")

STOPWORDS = {
    "find",
    "files",
    "file",
    "documents",
    "document",
    "that",
    "have",
    "has",
    "with",
    "containing",
    "word",
    "words",
    "the",
    "a",
    "an",
    "me",
    "show",
    "list",
    "all",
    "album",
    "make",
    "create",
    "of",
    "for",
    "about",
    "pics",
    "pictures",
    "photos",
    "on",
    "it",
    "my",
}


def normalize_query(text: str) -> str:
    tokens = [t for t in tokenize_text(text) if t not in STOPWORDS]
    return " ".join(tokens)


def serialize_entries(entries):
    return [entry.to_public_dict() for entry in entries]


def build_sources(entries, reference_query: str):
    tokens = tokenize_text(reference_query)
    if not tokens:
        return []
    return [{"path": e.relative_path, "score": e.score(tokens)} for e in entries]


def get_relevant_entries(question: str, limit: int = 5):
    normalized = normalize_query(question)
    query_for_search = normalized or question
    return file_index.search(query_for_search, limit=limit)


def generate_ai_response(question: str, entries):
    # If no model/key configured, return the simple fallback.
    if not OPENAI_API_KEY:
        if not entries:
            return "I couldn't find any relevant NAS files for that question."

        file_list = "\n".join(f"- {entry.relative_path}" for entry in entries)
        return (
            "I don't have access to a language model right now, "
            "but based on simple search I found these relevant files:\n\n"
            f"{file_list}"
        )

    # If the openai package couldn't be imported / client couldn't be created, instruct the developer.
    if OPENAI_API_KEY and client is None:
        return (
            "The server has an OPENAI_API_KEY configured but the Python 'openai' package is not available. "
            "Install it in your environment (pip install openai) and restart the server."
        )

    # Try RAG-based retrieval first if enabled
    rag_context_text = None
    if RAG_ENABLED and retrieve and format_context:
        try:
            chunks = retrieve(db_path=RAG_DB_PATH, query=question, openai_api_key=OPENAI_API_KEY, top_k=6, max_candidates=5000)
            rag_context_text, _ = format_context(chunks)
        except Exception:
            rag_context_text = None

    # Build fallback context from the top snippets if RAG didn't work
    context_lines = []
    for entry in entries[:3]:
        if entry.text_preview and entry.text_preview.strip():
            preview = entry.text_preview[:800]
        else:
            preview = "(This appears to be a scanned/image-based PDF without extractable text. OCR would be needed to read the content.)"
        context_lines.append(
            f"FILE: {entry.relative_path}\n"
            f"Name: {entry.original_name}\n"
            f"Category: {entry.category}\n"
            f"Preview: {preview}"
        )
    fallback_context_text = "\n\n".join(context_lines)
    
    # Use RAG context if available, otherwise fallback
    context_text = rag_context_text or fallback_context_text

    system_prompt = """You are a retrieval-augmented assistant that answers questions strictly using
the user's NAS files provided to you.

Rules:
1. Only use information that is explicitly present in the retrieved file content.
2. When the user asks for documents/files containing specific words or topics, list the matching files from the context provided.
3. If no relevant files are found in the context, respond with: "No relevant information found in the NAS."
4. Do not infer, assume, or fabricate any details beyond the retrieved files.
5. When applicable, cite the source file(s) using their relative file path(s).
6. Be concise and focus on actionable information.
7. If the question is not related to the NAS files, respond briefly and do not speculate.
8. If a file is a scanned PDF or image without extractable text, inform the user that
   Optical Character Recognition (OCR) is required to access its contents.
"""



    user_prompt = (
        f"Question: {question}\n\n"
        "Context files (may be partial):\n"
        f"{context_text}\n\n"
        "If you reference a file, include the filename in a 'Sources' section at the end."
    )

    try:
        # Use Chat Completions API
        # Use the new OpenAI client chat completions interface
        if client is None:
            return "The server has no OpenAI client configured."
        
        resp = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=512,
            temperature=0.2,
        )

        # Response is an object; try to extract the message content robustly
        content = None
        try:
            # openai>=1.x: resp.choices[0].message.content
            choices = getattr(resp, "choices", None) or (resp.get("choices") if isinstance(resp, dict) else None)
            if choices:
                first = choices[0]
                # support both object and dict shapes
                if hasattr(first, "message"):
                    content = getattr(first.message, "content", None)
                elif isinstance(first, dict):
                    content = first.get("message", {}).get("content") or first.get("text")
        except Exception:
            content = None

        if not content:
            return "The language model did not return an answer."

        return content.strip()
    except Exception as e:
        # Include a short error hint (do not leak API keys).
        tb = traceback.format_exc()
        print("OpenAI call failed:", tb)

        # Classify the error text (lowercase for simpler checks)
        err_type = type(e).__name__
        err_msg = str(e).lower()
        is_quota = (
            "insufficient_quota" in err_msg
            or "ratelimit" in err_type.lower()
            or "rate limit" in err_msg
            or "quota" in err_msg
        )

        # Try a local search fallback (use provided entries or re-run a local search)
        local_matches = entries or get_relevant_entries(question)

        if is_quota:
            if local_matches:
                file_list = "\n".join(f"- {entry.relative_path}" for entry in local_matches)
                return (
                    "The language model could not be reached due to account quota or rate limits. "
                    "I can't access the hosted LLM right now, but based on local search I found these files:\n\n"
                    f"{file_list}"
                )
            return (
                "The language model could not be reached due to account quota or rate limits. "
                "Check your OpenAI billing/plan settings or set OPENAI_MODEL to 'gpt-3.5-turbo' in the server environment for lower-cost testing."
            )

        # For non-quota errors, still try to offer local matches if available
        if local_matches:
            file_list = "\n".join(f"- {entry.relative_path}" for entry in local_matches)
            return (
                "I couldn't reach the external language model, but I found these local files that may help:\n\n"
                f"{file_list}"
            )

        return (
            "An error occurred while contacting the language model provider. "
            "Check server logs for details."
        )


def try_album_command(question: str):
    match = re.search(r"album(?: of| for)? (.+)", question, flags=re.IGNORECASE)
    if not match:
        return None

    subject = match.group(1).strip().rstrip(".!?")
    if not subject:
        return None

    query = normalize_query(subject) or subject
    picture_matches = file_index.search(query, category="Pictures", limit=20)
    if not picture_matches:
        return {
            "answer": f"I couldn't find any pictures related to '{subject}'. Try uploading a few first.",
            "sources": [],
            "files": [],
        }
    album_name = subject.title()
    # Instead of creating the album immediately, return a suggestion with matched files
    # The client can confirm to create the album via POST /albums
    return {
        "answer": f"I found {len(picture_matches)} pictures related to '{subject}'. Would you like me to create an album named '{album_name}'?",
        "sources": build_sources(picture_matches, query),
        "files": serialize_entries(picture_matches),
        "suggestion": {"name": album_name, "file_ids": [m.id for m in picture_matches]},
    }


def try_pictures_command(question: str):
    """Handle requests to show/list all pictures/images"""
    lowered = question.lower()
    # Check for picture/image listing requests
    if not any(word in lowered for word in ["picture", "image", "photo", "pic"]):
        return None
    if not any(phrase in lowered for phrase in ["show", "all", "my", "list", "get"]):
        return None
    
    # Get all pictures by filtering directly (search requires keywords)
    picture_matches = [entry for entry in file_index.list_files() if entry.category == "Pictures"]
    if not picture_matches:
        return {
            "answer": "You don't have any pictures uploaded yet. Try uploading some images first!",
            "sources": [],
            "files": [],
        }
    
    answer = f"I found {len(picture_matches)} picture(s) in your NAS. Here they are!"
    return {
        "answer": answer,
        "sources": [],
        "files": serialize_entries(picture_matches),
    }


def try_summarize_pdfs_command(question: str):
    """Handle requests to summarize all PDFs"""
    lowered = question.lower()
    if "summarize" not in lowered and "summary" not in lowered:
        return None
    if "pdf" not in lowered:
        return None
    
    # Get all PDF files
    pdf_files = [entry for entry in file_index.list_files() if entry.extension.lower() == ".pdf"]
    if not pdf_files:
        return {
            "answer": "You don't have any PDF files uploaded yet.",
            "sources": [],
            "files": [],
        }
    
    # Don't intercept - let it fall through to the LLM with all PDFs in context
    # Return None so the chat endpoint processes it normally with AI
    return None


def try_find_command(question: str):
    lowered = question.lower()
    if "find" not in lowered:
        return None
    if "file" not in lowered and "document" not in lowered and "pic" not in lowered and "photo" not in lowered:
        return None

    cleaned = normalize_query(question)
    query = cleaned or question
    matches = file_index.search(query, limit=12)
    if not matches:
        return {
            "answer": f"I couldn't find any files related to '{question}'.",
            "sources": [],
            "files": [],
        }

    file_lines = "\n".join(f"- {m.original_name} ({m.relative_path})" for m in matches[:5])
    answer = f"Here are the top matches I found:\n{file_lines}"
    return {
        "answer": answer,
        "sources": build_sources(matches, query),
        "files": serialize_entries(matches),
    }


@app.get("/files")
def list_files():
    entries = file_index.list_files()
    files = []
    for entry in entries:
        public_dict = entry.to_public_dict()

        # Try DB first
        conn = get_db_conn()
        cur = conn.cursor()
        cur.execute("SELECT tags FROM files WHERE id = ?", (entry.id,))
        row = cur.fetchone()
        conn.close()

        if row and row["tags"]:
            tags = row["tags"].split(",")
        else:
            # Fallback: classify again
            path = STORAGE_PATH / entry.relative_path
            try:
                tags = classify_any(path)   # 👈 use unified classifier
                # Optionally save back into DB so next time it's cached
                conn = get_db_conn()
                cur = conn.cursor()
                cur.execute("UPDATE files SET tags = ? WHERE id = ?", (",".join(tags), entry.id))
                conn.commit()
                conn.close()
            except Exception as e:
                print(f"⚠️ Classification failed for {entry.original_name}: {e}")
                tags = ["image"]

        public_dict["tags"] = tags
        files.append(public_dict)

    return jsonify({"files": files})
    # return jsonify({"files": serialize_entries(entries)})


@app.post("/files")
def upload_file():
    # If UPLOAD_API_KEY is set, require clients to pass it in X-API-KEY header
    if UPLOAD_API_KEY:
        provided = request.headers.get("X-API-KEY")
        if provided != UPLOAD_API_KEY:
            return jsonify({"error": "Unauthorized - missing or invalid API key"}), 401

    # Pre-check Content-Length if available to avoid saving huge uploads
    content_length = request.content_length
    if content_length and content_length > MAX_UPLOAD_SIZE:
        return jsonify({"error": "Payload too large"}), 413

    if "file" not in request.files:
        return jsonify({"error": "Missing file field"}), 400
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400
    try:
        entry = file_index.add_file(file)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    # 👇 Run AI classifier for images
    path = STORAGE_PATH / entry.relative_path
    if entry.category == "Images":
        try:
            tags = classify_any(path)
        except Exception as e:
            print(f"⚠️ Classification failed: {e}")
            tags = ["image"]
        
        # Save tags into DB
        conn = get_db_conn()
        cur = conn.cursor()
        cur.execute("UPDATE files SET tags = ? WHERE id = ?", (",".join(tags), entry.id))
        conn.commit()
        conn.close()
        
        # Add tags to response
        public_dict = entry.to_public_dict()
        public_dict["tags"] = tags
    else:
        public_dict = entry.to_public_dict()
    
    # Auto-index documents for RAG if enabled
    if RAG_ENABLED and entry.category == "Documents" and entry.extension.lower() in {".pdf", ".txt", ".md", ".csv", ".json", ".log"}:
        try:
            from rag.ingest import ingest_file
            abs_path = STORAGE_PATH / entry.relative_path
            if abs_path.exists():
                ingest_file(
                    db_path=RAG_DB_PATH,
                    file_id=entry.id,
                    rel_path=entry.relative_path,
                    abs_path=abs_path,
                    openai_api_key=OPENAI_API_KEY,
                    allow_ocr=RAG_ALLOW_OCR
                )
                print(f"✅ RAG indexed uploaded file: {entry.original_name}")
        except Exception as e:
            print(f"⚠️  RAG indexing failed for {entry.original_name}: {e}")
            # Don't fail the upload if RAG indexing fails

    return jsonify({"file": public_dict}), 201

@app.delete("/files/<file_id>")
def delete_file(file_id):
    deleted = file_index.delete_file(file_id)
    if not deleted:
        return jsonify({"error": "File not found"}), 404

    conn = get_db_conn()
    cur = conn.cursor()
    # Remove file entry
    cur.execute("DELETE FROM files WHERE id = ?", (file_id,))
    # Remove any album associations
    cur.execute("DELETE FROM album_files WHERE file_id = ?", (file_id,))
    conn.commit()
    conn.close()

    return jsonify({"status": "deleted"})

@app.get("/files/<file_id>/raw")
def download_file(file_id):
    entry = file_index.get_file(file_id)
    if not entry:
        return jsonify({"error": "File not found"}), 404
    path = STORAGE_PATH / entry.relative_path
    if not path.exists():
        return jsonify({"error": "File not found"}), 404
    return send_file(path, mimetype=entry.mime_type, download_name=entry.original_name, as_attachment=False)


@app.get("/albums")
def list_albums():
    return jsonify({"albums": file_index.list_albums()})


@app.post("/albums")
def create_album():
    # If UPLOAD_API_KEY is set, require clients to pass it in X-API-KEY header
    if UPLOAD_API_KEY:
        provided = request.headers.get("X-API-KEY")
        if provided != UPLOAD_API_KEY:
            return jsonify({"error": "Unauthorized - missing or invalid API key"}), 401

    payload = request.get_json() or {}
    name = (payload.get("name") or "").strip()
    query = (payload.get("query") or name or "").strip()
    file_ids = payload.get("file_ids") or []
    if not name:
        return jsonify({"error": "Album name is required"}), 400
    if not file_ids:
        matches = file_index.search(query or name, category="Pictures", limit=20)
        file_ids = [m.id for m in matches]
    if not file_ids:
        return jsonify({"error": "No matching files to add to the album"}), 400
    album = file_index.create_album(name, file_ids, query or name)
    return jsonify({"album": album})


@app.post("/chat")
def chat():
    data = request.get_json() or {}
    question = (data.get("message") or "").strip()
    if not question:
        return jsonify({"answer": "Please provide a question.", "sources": []})

    # Quick command handlers for common actions
    for handler in (try_summarize_pdfs_command, try_pictures_command, try_album_command, try_find_command):
        result = handler(question)
        if result:
            return jsonify(result)

    # Check if user wants to summarize PDFs - get ALL PDFs instead of top 3
    lowered = question.lower()
    if ("summarize" in lowered or "summary" in lowered) and "pdf" in lowered:
        entries = [entry for entry in file_index.list_files() if entry.extension.lower() == ".pdf"][:10]
    else:
        entries = get_relevant_entries(question)
    answer = generate_ai_response(question, entries)
    sources = build_sources(entries, normalize_query(question) or question)

    # If RAG is enabled, try to add chunk-level citations
    if RAG_ENABLED and retrieve and format_context:
        try:
            chunks = retrieve(db_path=RAG_DB_PATH, query=question, openai_api_key=OPENAI_API_KEY, top_k=6, max_candidates=5000)
            
            # Filter chunks by confidence threshold
            high_confidence_chunks = [c for c in chunks if c.score >= RAG_MIN_SCORE]
            
            if high_confidence_chunks:
                _, rag_sources = format_context(high_confidence_chunks)
                print(f"🔍 RAG_USED=True | Question: {question[:50]}... | Citations: {len(rag_sources)} (filtered from {len(chunks)})")
                return jsonify({"answer": answer, "sources": rag_sources, "files": serialize_entries(entries)})
            else:
                # No chunks meet confidence threshold - fall back to keyword search
                print(f"🔍 RAG_USED=False | No chunks above threshold {RAG_MIN_SCORE} (best: {chunks[0].score if chunks else 0:.3f}), using keyword fallback")
                # Let it fall through to keyword search below instead of returning empty
        except Exception as e:
            print(f"⚠️  RAG_USED=False (error: {e}) | Falling back to keyword search")

    print(f"🔍 RAG_USED=False | Using keyword search fallback")
    return jsonify({"answer": answer, "sources": sources, "files": serialize_entries(entries)})


@app.post("/rag/reindex")
def rag_reindex():
    """Manually trigger RAG reindexing of all documents"""
    if UPLOAD_API_KEY:
        provided = request.headers.get("X-API-KEY")
        if provided != UPLOAD_API_KEY:
            return jsonify({"error":"Unauthorized"}), 401
    if not (RAG_ENABLED and ingest_all):
        return jsonify({"error":"RAG not enabled"}), 400

    files = [(e.id, e.relative_path, STORAGE_PATH / e.relative_path)
             for e in file_index.list_files()
             if e.category == "Documents" and (STORAGE_PATH / e.relative_path).exists()]

    result = ingest_all(
        db_path=RAG_DB_PATH,
        files=files,
        openai_api_key=OPENAI_API_KEY,
        allow_ocr=RAG_ALLOW_OCR,
        max_seconds=25,
    )
    return jsonify({"status":"ok","indexed":result.indexed,"skipped":result.skipped,"errors":result.errors})


@app.get("/rag/status")
def rag_status():
    """Get RAG system health status"""
    if not RAG_ENABLED:
        return jsonify({"enabled": False})
    
    try:
        import sqlite3
        conn = sqlite3.connect(RAG_DB_PATH)
        cur = conn.cursor()
        
        # Count indexed documents
        cur.execute("SELECT COUNT(*) FROM rag_files WHERE status='ok'")
        docs_count = cur.fetchone()[0]
        
        # Count total chunks
        cur.execute("SELECT COUNT(*) FROM rag_chunks")
        chunks_count = cur.fetchone()[0]
        
        # Get last indexed timestamp
        cur.execute("SELECT MAX(indexed_at) FROM rag_files")
        last_indexed = cur.fetchone()[0]
        
        # Get status breakdown
        cur.execute("SELECT status, COUNT(*) FROM rag_files GROUP BY status")
        status_breakdown = dict(cur.fetchall())
        
        conn.close()
        
        return jsonify({
            "enabled": True,
            "documents_indexed": docs_count,
            "chunks": chunks_count,
            "last_indexed": last_indexed,
            "status_breakdown": status_breakdown,
            "ocr_enabled": RAG_ALLOW_OCR
        })
    except Exception as e:
        return jsonify({"enabled": True, "error": str(e)}), 500


@app.post("/files/<file_id>/share")
def create_share_link(file_id):
    """Generate a shareable link for a file"""
    entry = file_index.get_file(file_id)
    if not entry:
        return jsonify({"error": "File not found"}), 404
    
    # Generate a unique share token
    share_token = str(uuid.uuid4())
    expiry = request.get_json().get("expiry_hours", 24)  # Default 24 hours
    
    # In a real app, store this in a database with expiry time
    # For now, just return the share link
    share_link = f"{request.host_url}share/{share_token}"
    
    return jsonify({
        "share_link": share_link,
        "token": share_token,
        "expires_in_hours": expiry,
        "file_name": entry.original_name
    })


if __name__ == "__main__":
    if OPENAI_API_KEY:
        print("Backend API key loaded from environment (hidden).")
    else:
        print("No backend API key found in environment.")
    
    # Safe port parsing with fallback
    try:
        port = int(os.getenv("PORT", "5001"))
    except ValueError:
        print("Warning: Invalid PORT value, using default 5001")
        port = 5001
    
    print(f"Starting server on http://0.0.0.0:{port}")
    # Use a production WSGI server (gunicorn) for deployment
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)
