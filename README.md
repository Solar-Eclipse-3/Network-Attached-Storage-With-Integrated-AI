# 📦 Network-Attached Storage with Integrated AI

A full‑stack NAS platform built with **Flask + React**, featuring rich file uploads, smart search, and an integrated AI assistant (FileWizardAI) that can locate, filter, and organize your files using natural language.

This project demonstrates backend API design, frontend UI development, file storage architecture, and AI‑powered search — all wrapped in a clean, modern web interface.

---

# 🚀 Running the Project

This project includes both a **Flask backend** (file storage, indexing, and FileWizardAI logic) and a **React frontend** (dashboard, previews, and AI chat interface). Follow these steps to run everything locally.

---

## 🖥️ Backend Setup (Flask + FileWizardAI)

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
python chatbot_server.py
```

Backend runs on:

```
http://localhost:5000
```

---

## 🌐 Frontend Setup (React + FileWizardAI UI)

The frontend includes:

- File upload dashboard  
- File previews (images, videos, PDFs, text)  
- Filters + instant search  
- Chatbot UI for FileWizardAI  
- Album viewer and file chips  

```bash
npm install
npm run dev
```

Frontend runs on:

```
http://localhost:5173
```

---

# 🧠 My Contributions: FileWizardAI + Backend + Frontend

I was responsible for designing and implementing the **FileWizardAI system**, including both the backend logic and the frontend integration.

## 🔧 Backend (Flask)

- Built the FileWizardAI engine that interprets natural‑language commands  
- Implemented search logic combining keyword matching + AI responses  
- Created backend routes for:  
  - `/chat` (AI assistant)  
  - `/files` (upload, list, delete, metadata)  
  - `/albums` (create + list albums)  
- Integrated OpenAI responses with local file indexing  
- Ensured the system works **with or without** an API key (fallback mode)

## 🎨 Frontend (React)

- Developed the chat interface for FileWizardAI  
- Connected the UI to backend APIs for chat, file operations, and album creation  
- Built dynamic components for:  
  - File previews  
  - File chips  
  - Album displays  
  - Chatbot message formatting  
- Improved error handling and user feedback  
- Ensured smooth request/response flow between UI → backend → UI  

---

# ⚠️ Deployment Requirements

This app requires a persistent server environment:

- ✅ Persistent file storage for uploads  
- ✅ SQLite database for file indexing  
- ✅ Long-running server (not serverless)

**Compatible platforms:** Railway (with volumes), Render, VPS, self-hosted  
**NOT compatible:** Vercel, AWS Lambda, Azure Functions, or other serverless platforms  

---

# ✨ Features

- Upload/download/list/delete files from a web dashboard or CLI  
- Accepts images, videos, PDFs, docs, and plain-text formats  
- File previews (images, videos, inline text + PDF iframe)  
- Dark/light UI theme, per-type filters, and instant search  
- **FileWizardAI chatbot** that can:  
  - Search your NAS using natural language  
  - Build picture albums  
  - Group files by type or content  
- JSON API for files, albums, and chat  
- CLI client for scripted operations  

---

# 🖥️ Using the Web Dashboard & Chatbot

- Upload files via the dashboard  
- Files are stored under `storage/uploads/` and indexed in `storage/file_index.json`  
- Use filters or search to narrow results  
- Click a file card for preview or download  
- Use FOCA 🦭 chatbot to:  
  - Search files  
  - Create albums  
  - Ask general NAS questions  

### Example Commands

- `find the files that have the word report`  
- `make me an album of my graduation pics`  

With an OpenAI key, FileWizardAI uses GPT to generate richer answers.  
Without a key, it falls back to local keyword search.

---

# 🔌 HTTP API

The Flask server exposes several JSON endpoints (the React dev server proxies them under `/api`):

| Method | Endpoint | Description |  
|--------|--------------------|-------------|  
| GET | `/files` | List all indexed files and metadata |  
| POST | `/files` | Upload a file (`multipart/form-data` field named `file`) |  
| DELETE | `/files/<id>` | Delete a stored file and its metadata entry |  
| GET | `/files/<id>/raw` | Stream/download the raw file contents |  
| GET | `/albums` | List saved albums |  
| POST | `/albums` | Create an album (`name`, optional `query` or `file_ids`) |  
| POST | `/chat` | Ask the NAS assistant a question or command |  

---

# 🧪 CLI Usage (Optional)

```bash
python nas_client.py upload <file_path>
python nas_client.py download <filename>
python nas_client.py list
python nas_client.py delete <filename>
```

---

# 📁 Supported File Types

- Text/markdown/log (`.txt`, `.md`, `.log`, `.csv`, `.json`)  
- PDF (`.pdf`)  
- Documents (`.doc`, `.docx`)  
- Images (`.png`, `.jpg`, `.jpeg`, `.gif`, `.bmp`, `.webp`)  
- Videos (`.mp4`, `.mkv`, `.avi`, `.mov`, `.wmv`, `.flv`, `.webm`)  

---

# 🔐 Security Notes

This project is for demos/learning.  
For production use, add:

- Authentication  
- HTTPS  
- Access control  
- Backups  
- Monitoring  
