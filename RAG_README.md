# RAG (Retrieval-Augmented Generation) System

## Overview

This project now includes a complete RAG system that provides semantic search capabilities for documents stored in your NAS. Instead of simple keyword matching, the chatbot can now understand the meaning of questions and retrieve relevant information from uploaded documents.

## What Was Implemented

### Core Features ✅

1. **Semantic Search**
   - Uses OpenAI embeddings (text-embedding-3-small) to understand document meaning
   - Finds relevant information even when exact keywords don't match
   - Example: Asking "tell me about robots" finds content about "robotics" and "automation"

2. **Auto-Index on Upload**
   - Documents are automatically indexed when uploaded
   - No manual reindexing needed
   - Immediate searchability (within seconds of upload)

3. **Confidence Threshold**
   - Filters low-quality results (configurable via `RAG_MIN_SCORE`)
   - Returns "No relevant information found" instead of hallucinating
   - Default threshold: 0.33 (adjustable in `.env`)

4. **Health Monitoring**
   - `GET /rag/status` endpoint shows:
     - Number of documents indexed
     - Total chunks in database
     - Last indexing timestamp
     - OCR status
     - Status breakdown (ok/empty/error)

5. **Smart Document Processing**
   - Chunks documents into 2500-character segments with 300-char overlap
   - Preserves page information for PDFs
   - Supports: `.pdf`, `.txt`, `.md`, `.csv`, `.json`, `.log`

6. **OCR Support (Optional)**
   - Framework ready for scanned PDF processing
   - Requires system tools: `tesseract`, `poppler`
   - See `OCR_SETUP.md` for installation instructions
   - Currently disabled (works great without it)

## Architecture

```
rag/
├── __init__.py          # Module initialization
├── db.py                # SQLite database management
├── chunking.py          # Text splitting with overlap
├── embeddings.py        # OpenAI embeddings API
├── extract.py           # Text extraction from PDFs/files
├── ingest.py            # Document ingestion pipeline
├── retrieve.py          # Semantic search & retrieval
└── ocr.py               # OCR for scanned PDFs (optional)
```

### Database Schema

**rag_files table:**
- `file_id` - Unique identifier
- `rel_path` - Relative path in storage
- `mtime` - Last modified time
- `indexed_at` - Timestamp of indexing
- `status` - ok/empty/error
- `error` - Error message if failed

**rag_chunks table:**
- `id` - Auto-increment primary key
- `file_id` - Foreign key to rag_files
- `rel_path` - Document path (indexed)
- `page` - Page number (for PDFs)
- `chunk_index` - Sequential chunk number
- `text` - Chunk content
- `embedding` - Vector embedding (BLOB, numpy array)
- `dim` - Embedding dimension (1536)
- `updated_at` - Timestamp

## Configuration

Add these to your `.env` file:

```env
# Enable RAG system
RAG_ENABLED=1

# OCR for scanned PDFs (0=disabled, 1=enabled)
# Requires: brew install tesseract poppler
RAG_OCR=0

# Embedding model
RAG_EMBED_MODEL=text-embedding-3-small

# Minimum confidence score (0.0-1.0)
# Lower = more results, Higher = more relevant
RAG_MIN_SCORE=0.33

# OpenAI API key (required)
OPENAI_API_KEY=your-key-here
```

## How It Works

### 1. Upload Flow
```
User uploads document
    ↓
File saved to storage/
    ↓
Document auto-indexed (if RAG_ENABLED)
    ↓
Text extracted & chunked
    ↓
Embeddings generated via OpenAI
    ↓
Stored in SQLite (data/rag.db)
    ↓
Immediately searchable
```

### 2. Query Flow
```
User asks question
    ↓
Question embedded via OpenAI
    ↓
Cosine similarity search
    ↓
Filter by RAG_MIN_SCORE threshold
    ↓
Retrieve top 6 chunks
    ↓
Format context with citations
    ↓
Send to chatbot with source references
```

## API Endpoints

### Health Check
```bash
GET /rag/status

Response:
{
  "enabled": true,
  "ocr_enabled": false,
  "documents_indexed": 8,
  "chunks": 691,
  "last_indexed": "2025-12-15T22:21:35.136801",
  "status_breakdown": {
    "ok": 8,
    "empty": 1
  }
}
```

### Manual Reindex
```bash
POST /rag/reindex
Content-Type: application/json

{
  "time_limit_sec": 60  # Optional, default: 30
}

Response:
{
  "indexed": 5,
  "skipped": 3,
  "total_chunks": 691
}
```

### Chat with RAG
```bash
POST /chat
Content-Type: application/json

{
  "message": "What is gradient descent?"
}

Response:
{
  "answer": "Gradient descent is an optimization algorithm...",
  "sources": [
    {
      "file": "ml_notes.pdf",
      "page": 3,
      "chunk": 2,
      "score": 0.74
    }
  ]
}
```

## Current Status

### ✅ Working Features
- Semantic search: **691 chunks indexed** from 8 documents
- Auto-index on upload
- Confidence threshold filtering
- Health monitoring endpoint
- Manual reindex capability
- Graceful error handling
- Text-based PDFs fully supported

### ⏳ Optional Enhancements
- **OCR**: Code ready, requires system tools (see `OCR_SETUP.md`)
- **Actions Framework**: Intent detection & confirmation gates (Step 3)
- **Rate Limiting**: Production hardening (Step 4)

## Testing

### Test Semantic Search
```bash
# Upload a document
curl -X POST http://localhost:5001/files \
  -F "file=@your-document.pdf"

# Ask a question
curl -X POST http://localhost:5001/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What does this document say about X?"}'
```

### Test Confidence Threshold
```bash
# Ask an irrelevant question
curl -X POST http://localhost:5001/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is the capital of France?"}'

# Should return:
{
  "answer": "No relevant information found in the NAS.",
  "sources": []
}
```

### Check System Health
```bash
curl http://localhost:5001/rag/status | python3 -m json.tool
```

## Troubleshooting

### RAG Not Working?
1. Check `.env` has `RAG_ENABLED=1`
2. Verify `OPENAI_API_KEY` is set
3. Check `/rag/status` endpoint
4. Look for errors in server logs

### No Search Results?
1. Check `RAG_MIN_SCORE` - try lowering to 0.2
2. Verify documents are indexed: `curl http://localhost:5001/rag/status`
3. Manually reindex: `curl -X POST http://localhost:5001/rag/reindex`

### OCR Not Working?
1. OCR is **optional** - system works without it
2. See `OCR_SETUP.md` for installation
3. Check `/rag/status` shows `ocr_enabled: true`

## Performance

### Current Metrics
- **Documents**: 8 indexed
- **Chunks**: 691 total
- **Index Time**: ~3 seconds on startup (incremental)
- **Query Time**: <1 second for semantic search
- **Storage**: ~5MB (SQLite database)

### Scalability
- Handles hundreds of documents efficiently
- SQLite adequate for <10,000 documents
- Consider vector database (Pinecone, Weaviate) for production scale

## Dependencies

### Python Packages
```
numpy>=1.24.0,<2.0.0
pytesseract>=0.3.10      # OCR support
pdf2image>=1.16.0        # OCR support
pillow>=10.0.0           # OCR support
```

### System Tools (Optional - for OCR)
- `tesseract` - OCR engine
- `poppler` - PDF rendering
- Install: `brew install tesseract poppler`

## What's Next?

### Immediate (Ready to Demo)
- ✅ Test with various document types
- ✅ Adjust `RAG_MIN_SCORE` based on results
- ✅ Prepare demo queries

### Future Enhancements
- **Step 3**: Actions framework (create albums, organize files)
- **Step 4**: Production hardening (rate limiting, logging)
- **Step 5**: UI improvements (show source snippets)

## Git Commits

This RAG system was implemented in these commits:

```
a6f04b2 - chore: ignore temp scripts and backup files
620fab4 - docs: add OCR setup instructions and improve error messages  
d89999e - fix: return empty sources when confidence threshold not met
8139efb - feat: implement RAG system with semantic search
91d1456 - chore: add .nvmrc file to specify Node.js version
```

All commits pushed to: `feature/add-chatbot-backend-ui-202511231910-squashed`

## Security Notes

- ✅ `.env` file excluded from git (contains API key)
- ✅ No API keys committed to repository
- ✅ Database stored locally (not committed)
- ✅ File uploads respect `MAX_UPLOAD_SIZE`

## Credits

Implemented: December 15, 2025
Developer: GitHub Copilot + Solar-Eclipse-3
Framework: Flask + OpenAI + SQLite
