#!/bin/bash
# Setup script for McDonalds-McNuggets NAS application
# Run this on a new machine or Codespace

set -e  # Exit on error

echo "🚀 Setting up McDonalds-McNuggets NAS..."
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    
    # Try to use GitHub Codespace secret if available
    if [ ! -z "$OPENAI_API_KEY" ]; then
        echo "✅ Using OPENAI_API_KEY from environment"
        cat > .env << EOF
# OpenAI API Configuration (from Codespace secret)
OPENAI_API_KEY=$OPENAI_API_KEY
OPENAI_MODEL=gpt-3.5-turbo

# Optional: Upload API key for additional security
UPLOAD_API_KEY=
EOF
    else
        # Create template for manual setup
        cat > .env << 'EOF'
# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-3.5-turbo

# Optional: Upload API key for additional security
UPLOAD_API_KEY=
EOF
        echo "⚠️  IMPORTANT: Edit .env and add your OpenAI API key!"
        echo "   Run: nano .env (or use any text editor)"
        echo "   Or ask the project owner for access to the shared key"
        echo ""
    fi
else
    echo "✅ .env file already exists"
fi

# Install Node.js dependencies
echo "📦 Installing Node.js dependencies..."
npm install
echo ""

# Setup Python virtual environment
echo "🐍 Setting up Python virtual environment..."
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment and install dependencies
echo "📦 Installing Python dependencies..."
source .venv/bin/activate
pip install --upgrade pip
pip install flask flask-cors python-dotenv openai PyPDF2 pdf2image pillow pytesseract
echo ""

# Create storage directories
echo "📁 Creating storage directories..."
mkdir -p storage/uploads
mkdir -p storage/files
mkdir -p data
echo "✅ Storage directories created"
echo ""

echo "✅ Setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Edit .env and add your OpenAI API key:"
echo "   nano .env"
echo ""
echo "2. Start the application:"
echo "   npm run dev:all"
echo ""
echo "3. Open your browser to:"
echo "   http://localhost:5173"
echo ""
