#!/bin/bash

# Start Backend and Frontend Servers

echo "🚀 Starting Smart NAS Application..."
echo ""

# Activate virtual environment
source venv/bin/activate

# Start backend in background
echo "📦 Starting Backend Server (port 5001)..."
python chatbot_server.py &
BACKEND_PID=$!
echo "Backend PID: $BACKEND_PID"

# Wait for backend to start
sleep 3

# Check if backend started successfully
if curl -s http://localhost:5001/rag/status > /dev/null 2>&1; then
    echo "✅ Backend is running!"
else
    echo "❌ Backend failed to start. Check errors above."
    exit 1
fi

echo ""
echo "🌐 Application URLs:"
echo "   Backend API: http://localhost:5001"
echo "   RAG Status:  http://localhost:5001/rag/status"
echo ""
echo "📝 To start the frontend, open another terminal and run:"
echo "   cd '/Users/huli/Smart NAS/McDonalds-McNuggets-1'"
echo "   nvm use 22"
echo "   npm run dev"
echo ""
echo "Press Ctrl+C to stop the backend server"
echo ""

# Wait for Ctrl+C
wait $BACKEND_PID
