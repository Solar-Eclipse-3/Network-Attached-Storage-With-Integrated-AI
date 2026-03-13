# WARNING: This Vercel serverless configuration does NOT work for this app!
# The app requires:
# - Persistent file storage (for uploads)
# - SQLite database (not supported in serverless)
# - Long-running Flask server
#
# This file is kept for reference only.
# To run the app, use the local setup: python chatbot_server.py

# Lazy import to avoid initialization issues in serverless environments
def handler(request, context=None):
    from chatbot_server import app
    return app(request, context)
