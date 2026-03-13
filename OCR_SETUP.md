# OCR Setup Instructions

## Overview

The RAG system supports OCR (Optical Character Recognition) for scanned PDFs. This is **optional** - the system works perfectly without OCR for text-based PDFs and documents.

## Current Status

OCR is **disabled** by default (`RAG_OCR=0` in `.env`). When you try to index a scanned PDF, it will be skipped with a warning.

## How to Enable OCR

### Prerequisites

OCR requires two system tools:
- **tesseract** - OCR engine
- **poppler** - PDF rendering utilities

### Installation

#### macOS (Homebrew)

```bash
brew install tesseract poppler
```

**Note**: This requires up-to-date Xcode Command Line Tools. If you encounter build errors:

```bash
# Update Command Line Tools
sudo rm -rf /Library/Developer/CommandLineTools
sudo xcode-select --install

# Or use the App Store to update Xcode
```

#### Alternative: Docker (Recommended for Demo)

If system installation fails, you can run OCR in a Docker container:

```bash
# Pull an image with OCR tools pre-installed
docker pull jbarlow83/ocrmypdf

# Or create a simple Dockerfile
FROM python:3.11-slim
RUN apt-get update && apt-get install -y tesseract-ocr poppler-utils
```

#### Linux (apt)

```bash
sudo apt-get install tesseract-ocr poppler-utils
```

### Enable OCR in Config

After installing system tools, edit `.env`:

```env
RAG_OCR=1
```

Restart the server:

```bash
pkill -f chatbot_server
python chatbot_server.py
```

### Verify OCR is Working

Check the health endpoint:

```bash
curl -s http://127.0.0.1:5001/rag/status | python3 -m json.tool
```

Expected output:
```json
{
  "ocr_enabled": true,
  ...
}
```

### Test with a Scanned PDF

1. Upload a scanned PDF (image-only PDF)
2. Ask a question about its content
3. Verify the answer includes information from the PDF

## Troubleshooting

### "tesseract is not installed"

The system cannot find the `tesseract` command. Make sure:
- You ran `brew install tesseract` successfully
- The installation directory is in your PATH
- Check with: `which tesseract`

### "poppler is not installed"

The system cannot find `pdftoppm` (part of poppler). Make sure:
- You ran `brew install poppler` successfully
- Check with: `which pdftoppm`

### Homebrew Build Errors

If `brew install` fails due to compiler errors:

**Option 1**: Update your system tools (recommended)
```bash
sudo rm -rf /Library/Developer/CommandLineTools
sudo xcode-select --install
```

**Option 2**: Use Docker (see above)

**Option 3**: Disable OCR and document it
- Keep `RAG_OCR=0` in `.env`
- The `/rag/status` endpoint will show `"ocr_enabled": false`
- Add a note: "OCR available as optional enhancement - requires system tools"

## Why OCR is Optional

Most use cases don't need OCR:
- Modern PDFs are text-based (searchable)
- Text files, markdown, code - all work without OCR
- OCR adds system dependencies and complexity

OCR is only needed for:
- Scanned documents (paper → PDF)
- Screenshots saved as PDFs
- Old digitized books

## Production Considerations

For production deployment:
- Use Docker with pre-installed OCR tools
- Or document OCR as an optional feature
- Monitor OCR failures separately from regular indexing failures
