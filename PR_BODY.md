Title: feat: Add Chatbot UI, UploadManager, backend chat and file indexing

Summary

This branch adds a Chatbot UI and UploadManager plus a Flask backend that handles file uploads, indexing, and chat queries. The backend uses a local-file search fallback when an OpenAI key is not configured or the LLM call fails.

Key changes

- Frontend: `src/Chatbot.jsx`, `src/UploadManager.jsx`, integrated into `src/App.jsx`.
- Backend: `chatbot_server.py`, `file_index.py` with file indexing, album support, and chat endpoints.
- Safe JSON parsing: Frontend now uses robust JSON parsing to avoid crashes on empty or invalid responses.
- Improved error messaging: Upload and chat flows now surface clear "backend not reachable" guidance and surface upload errors to the user.
- CORS dependency: added `flask-cors` to `requirments.txt` (backend dependency required for cross-origin requests during dev).
- Dev docs: `DEV_SETUP.md` updated with Node >=20.19 requirement and `gh` CLI instructions.

Notes & testing

- Uploaded files are stored under `storage/uploads/` and indexed in `data/files.db`.
- I ran an end-to-end upload test (multipart POST) — the file appears in `GET /files` and via the Vite dev proxy.
- I also started the dev servers locally (Vite + Flask) and validated the fallback chat response when OpenAI is not configured.

Next steps

- Create a draft PR from branch `feature/add-chatbot-backend-ui-202511231910` to `main` and paste this body, or run:

```bash
# save body then run:
# gh pr create --base main --head feature/add-chatbot-backend-ui-202511231910 --title "feat: Add Chatbot UI, UploadManager, backend chat and file indexing" --body-file PR_BODY.md --draft
```

- Optional: upgrade Node locally to >=20.19 (nvm recommended) to avoid Vite runtime warnings.

-- Automated note by Copilot agent
