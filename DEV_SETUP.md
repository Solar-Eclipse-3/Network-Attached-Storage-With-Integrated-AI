Local development notes — HTTPS & API proxy

This project already uses a Vite dev proxy so the frontend can call `/api/*` and Vite forwards requests to the Flask backend running at `http://127.0.0.1:5001`.

Environment
- Frontend base API: `VITE_API_BASE` (defaults to `/api`).

Scripts added
- `npm run dev` — start Vite (HTTP)
- `npm run dev:host` — start Vite bound to network (HTTP)
- `npm run dev:https` — start Vite with HTTPS using certs at `./dev-certs/localhost.pem` and `./dev-certs/localhost-key.pem`
- `npm run dev:all` — runs frontend + backend together (uses `concurrently`)

How to enable HTTPS locally (optional)
1. Install mkcert (macOS/Homebrew):

```bash
brew install mkcert
brew install nss # only if you need Firefox support
mkcert -install
```

2. Generate certs for localhost and save them into the repo directory `dev-certs/`:

```bash
mkdir -p dev-certs
mkcert -cert-file dev-certs/localhost.pem -key-file dev-certs/localhost-key.pem localhost 127.0.0.1 ::1
```

3. Start Vite with HTTPS (uses the `dev:https` script):

```bash
nvm use 20.19
npm run dev:https
```

4. Open `https://localhost:5173/` in your browser. The cert is trusted locally by `mkcert`, so you should not see "Not secure" warnings.

Notes
- We added `dev-certs/` to `.gitignore` so your generated certs won't be committed.
- If you prefer not to install `mkcert`, use `localhost` (HTTP) during dev and you can still use the proxy to reach the backend via `/api`.

If you'd like, I can run the mkcert steps and start Vite with HTTPS for you — confirm and I'll proceed (it will modify your local trust store via mkcert).

Environment files
-----------------
For backend secrets (never commit real keys):

1. Copy `.env.example` to `.env` and fill values (e.g. `OPENAI_API_KEY=`).
2. `.env` is ignored by git by default; the server loads it via python-dotenv.

For frontend (client) env variables:

1. Copy `.env.local.example` to `.env.local` and set `VITE_API_BASE` or `VITE_API_KEY` as needed.
2. Vite exposes variables prefixed with `VITE_` to client code. Restart Vite after changes.

Node & GitHub CLI
------------------

This project requires Node.js >= 20.19 for development (Vite). Follow these steps to upgrade and install the `gh` CLI for creating PRs locally.

1. Install or switch Node via `nvm` (recommended):

```bash
nvm install 20.19
nvm use 20.19
node -v  # should show >= v20.19.0
```

2. Install GitHub CLI (`gh`) on macOS via Homebrew:

```bash
brew install gh
gh --version
```

3. Authenticate `gh` (interactive):

```bash
gh auth login
# Follow prompts to authenticate with your GitHub account (use the web flow or a token).
```

4. Create a draft PR (example command). Save the PR body to a file first if you want a long description:

```bash
cat > /tmp/pr_body.md <<'PR'
feat: Add Chatbot UI, UploadManager, backend chat and file indexing

This patch adds:
- Frontend `Chatbot` component and `UploadManager` for drag/drop uploads.
- Flask backend endpoints for `/chat`, `/files`, `/albums` and a local file index fallback when OpenAI is not configured or fails.
- `file_index.py` for indexing uploaded files and searching by content.
- Updated `.env.example` and `.gitignore` to avoid committing secrets and local data.

Notes:
- Rotate any exposed OpenAI keys; `.env` should not be committed.
- Vite dev server requires Node >= 20.19; the repo now includes an `engines` field in `package.json`.
PR

gh pr create --base main --head feature/add-chatbot-backend-ui-202511231910 --title "feat: Add Chatbot UI, UploadManager, backend chat and file indexing" --body-file /tmp/pr_body.md --draft
```

If you prefer a web flow, open this URL in your browser to start a new PR with the branch already selected:

```
https://github.com/Solar-Eclipse-3/McDonalds-McNuggets/pull/new/feature/add-chatbot-backend-ui-202511231910
```