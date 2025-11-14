#!/bin/bash
# Quick setup script for Zypher AI Logo Generator with new features

echo "🚀 Zypher AI Setup Script"
echo "========================="
echo ""

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✓ Python version: $PYTHON_VERSION"

# Create virtual environment
echo ""
echo "📦 Setting up virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "📥 Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo ""
echo "📥 Installing dependencies..."
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✓ All dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

# Check if .env exists
echo ""
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found"
    echo "📝 Creating .env from .env.example..."
    cp .env.example .env
    echo "✓ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env file and add your API keys:"
    echo "   - HUGGINGFACE_TOKEN"
    echo "   - MISTRAL_API_KEY"
    echo "   - BRAVE_SEARCH_API_KEY"
    echo "   - Firebase credentials"
else
    echo "✓ .env file exists"
fi

# Create necessary directories
echo ""
echo "📁 Creating directories..."
mkdir -p outputs
mkdir -p chat_logs
mkdir -p models/lora
echo "✓ Directories created"

# Check database
echo ""
if [ -f "data.db" ]; then
    echo "✓ SQLite database found"
else
    echo "⚠️  No database found (will be created on first run)"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your API keys:"
echo "   - Get Mistral API key: https://console.mistral.ai/api-keys/"
echo "   - Get Brave Search API key: https://brave.com/search/api/"
echo "   - Get Hugging Face token: https://huggingface.co/settings/tokens"
echo ""
echo "2. (Optional) Migrate to PostgreSQL:"
echo "   python migrate_to_postgres.py postgresql://user:pass@localhost/zypher_ai"
echo ""
echo "3. Run the application:"
echo "   python app_flask.py"
echo ""
echo "4. Access the app:"
echo "   Main app: http://localhost:7860"
echo "   Admin dashboard: http://localhost:7860/admin"
echo ""
echo "📖 For detailed setup instructions, see README_NEW_FEATURES.md"
