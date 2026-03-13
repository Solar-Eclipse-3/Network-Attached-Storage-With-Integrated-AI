# 📦 Network-Attached Storage with Integrated AI

A full‑stack NAS platform built with **Flask + React**, featuring rich file uploads, smart search, and an integrated AI assistant (FileWizardAI) that can locate, filter, and organize your files using natural language.

This project demonstrates backend API design, frontend UI development, file storage architecture, and AI‑powered search — all wrapped in a clean, modern web interface.

---

# 🚀 Running the Project

This project includes both a **Flask backend** (file storage, indexing, and FileWizardAI logic) and a **React frontend** (dashboard, previews, and AI chat interface). Follow these steps to run everything locally.

---

## 🖥️ 1. Backend Setup (Flask + FileWizardAI)

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt

#Start the backend server:
python chatbot_server.py

#Backend runs on http://localhost:5000

# 🌐 2. Frontend Setup (React + FileWizardAI UI)



<!-- # Network Attached Storage with Integrated AI

A simple NAS built with Flask + React that now supports rich file uploads, smart search, and a chatbot that can locate or group your files on demand.

## ⚠️ Deployment Requirements

**This app requires a persistent server environment:**
- ✅ **Persistent file storage** for uploads
- ✅ **SQLite database** for file indexing
- ✅ **Long-running server** (not serverless)

**Compatible platforms:** Railway (with volumes), Render, VPS, self-hosted  
**NOT compatible:** Vercel, AWS Lambda, Azure Functions, or other serverless platforms

## Features

- Upload/download/list/delete files from a web dashboard or CLI
- Accepts images, videos, PDFs, docs, and plain-text formats
- File previews (images, videos, inline text + PDF iframe)
- Dark/light UI theme, per-type filters, and instant search
- Chatbot (FOCA 🦭) that can search your NAS or build picture albums using natural language
- JSON API for files, albums, and chat—easy to integrate with other apps

## Setup

1. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```
2. Install backend dependencies:
   ```bash
   pip install -r requirments.txt   # note the existing filename spelling
   ```
3. (Optional) Copy `.env.example` to `.env` and set `OPENAI_API_KEY` if you want GPT answers.
4. Start the Flask chatbot/file server:
   ```bash
   python chatbot_server.py
   ```
5. Install frontend deps and launch Vite:
   ```bash
   npm install
   npm run dev
   ```
6. Open http://localhost:5173, sign up/log in, and start uploading files.

## Using the Web Dashboard & Chatbot

- Click **Upload File** to add pictures, videos, docs, or PDFs. Files are stored under `storage/uploads/` and indexed in `storage/file_index.json`.
- Use the sidebar filters or search box to narrow the grid. Click a card for a preview or the download link.
- Open the FOCA 🦭 chatbot to control everything with natural-language commands:
  - `find the files that have the word report` – returns matching documents and download links.
  - `make me an album of my graduation pics` – scans your pictures and creates a saved album.
  - Any general NAS question. With an OpenAI key configured the model answers using the indexed snippets; without a key you still get local keyword search results.
- The chatbot response shows the answer text, album info (if created), clickable file chips, and the underlying storage paths.

## HTTP API

The Flask server exposes several JSON endpoints (the React dev server proxies them under `/api`):

| Method | Endpoint           | Description                                                    |
| ------ | ------------------ | -------------------------------------------------------------- |
| GET    | `/files`           | List all indexed files and metadata.                            |
| POST   | `/files`           | Upload a file (`multipart/form-data` field named `file`).       |
| DELETE | `/files/<id>`      | Delete a stored file and its metadata entry.                    |
| GET    | `/files/<id>/raw`  | Stream/download the raw file contents.                          |
| GET    | `/albums`          | List saved albums.                                              |
| POST   | `/albums`          | Create an album (`name`, optional `query` or `file_ids`).       |
| POST   | `/chat`            | Ask the NAS assistant a question or command (search/album/etc). |

### CLI (optional)

`nas_client.py` still works for simple scripted operations:

```
python nas_client.py upload <file_path>
python nas_client.py download <filename>
python nas_client.py list
python nas_client.py delete <filename>
```

## Supported File Types

- Text/markdown/log (`.txt`, `.md`, `.log`, `.csv`, `.json`)
- PDF (`.pdf`)
- Documents (`.doc`, `.docx`)
- Images (`.png`, `.jpg`, `.jpeg`, `.gif`, `.bmp`, `.webp`)
- Videos (`.mp4`, `.mkv`, `.avi`, `.mov`, `.wmv`, `.flv`, `.webm`)

## Chatbot Tips

- Configure `OPENAI_API_KEY` + `OPENAI_MODEL` in `.env` to let GPT draft richer answers grounded in your files.
- Without a key the app falls back to local keyword search and still returns matching file links.
- Album commands prioritise pictures; delete/re-upload images to refresh the album contents.

## Security Notes

This project is for demos/learning. For production use, also include authentication, HTTPS, encryption, access control, and backups/monitoring. -->
