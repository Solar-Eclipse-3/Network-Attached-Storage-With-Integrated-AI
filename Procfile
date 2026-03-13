# NOTE: This requires a persistent server deployment (Railway, Render, etc.)
# NOT compatible with serverless (Vercel, AWS Lambda) due to SQLite + file storage
web: gunicorn chatbot_server:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120