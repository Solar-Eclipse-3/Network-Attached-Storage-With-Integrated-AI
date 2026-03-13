# McDonalds-McNuggets NAS Setup Guide

## Quick Start (New Machine/Codespace)

### Option 1: Automated Setup (Recommended)
```bash
chmod +x setup.sh
./setup.sh
```

Then edit `.env` to add your OpenAI API key:
```bash
nano .env
```

Start the app:
```bash
npm run dev:all
```

---

### Option 2: Manual Setup

#### 1. Create `.env` file
```bash
cp .env.example .env
```

Edit `.env` and add your OpenAI API key from https://platform.openai.com/api-keys

#### 2. Install Node.js dependencies
```bash
npm install
```

#### 3. Setup Python environment
```bash
# Create virtual environment
python3 -m venv .venv

# Activate it (macOS/Linux)
source .venv/bin/activate

# Or on Windows
.venv\Scripts\activate

# Install Python packages
pip install flask flask-cors python-dotenv openai PyPDF2
```

#### 4. Create storage directories
```bash
mkdir -p storage/uploads storage/files data
```

#### 5. Start the application
```bash
npm run dev:all
```

This starts:
- **Frontend**: http://localhost:5173
- **Backend**: http://127.0.0.1:5001

---

## Troubleshooting

### "Backend not reachable" error
- Make sure you ran `npm run dev:all` (not just `npm run dev`)
- Check that port 5001 is not in use
- Verify `.env` file exists with a valid `OPENAI_API_KEY`

### Python module errors
```bash
source .venv/bin/activate
pip install flask flask-cors python-dotenv openai PyPDF2
```

### Node version issues
This project requires Node.js 20.19+. Install via:
```bash
# Using nvm (recommended)
nvm install 20.19
nvm use 20.19
```

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | Yes | Your OpenAI API key for chatbot functionality |
| `OPENAI_MODEL` | No | Model to use (default: gpt-3.5-turbo) |
| `UPLOAD_API_KEY` | No | Optional API key for upload authentication |

---

## Sharing API Key with Team (Optional)

### For GitHub Codespaces:

**Repository Owner:**
1. Go to your repo on GitHub
2. Settings → Secrets and variables → Codespaces
3. Click "New repository secret"
4. Name: `OPENAI_API_KEY`
5. Value: Your OpenAI API key
6. Click "Add secret"

**Team Members:**
- Just run `./setup.sh` in Codespace
- The key will be automatically loaded from the secret
- No manual configuration needed!

### For Local Development:

**Option 1: Securely share via 1Password/LastPass**
- Store the `.env` file in a shared vault
- Team members download and place in project root

**Option 2: Direct share (less secure)**
- Send the API key via encrypted message (Signal, etc.)
- Never share via email or public channels
- Team members create their own `.env` file

---

## What Gets Installed

### Node.js (Frontend)
- Vite - Fast development server
- React - UI framework
- Framer Motion - Animations

### Python (Backend)
- Flask - Web framework
- Flask-CORS - Cross-origin support
- OpenAI - AI chatbot integration
- PyPDF2 - PDF text extraction

---

## Need Help?

Check `DEV_SETUP.md` for detailed development instructions.
