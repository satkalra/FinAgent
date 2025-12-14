#!/bin/bash

# FinAgent Backend Setup Script

echo "🚀 Setting up FinAgent Backend..."

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ uv is not installed. Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    echo "✅ uv installed successfully!"
fi

# Create virtual environment
echo "📦 Creating virtual environment with uv..."
uv venv

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source .venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
uv pip install -e .

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚙️  Creating .env file..."
    cp .env.example .env
    echo "⚠️  Please edit .env and add your OPENAI_API_KEY"
else
    echo "✅ .env file already exists"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "To activate the virtual environment manually:"
echo "  source .venv/bin/activate"
echo ""
echo "To run the backend:"
echo "  python -m app.main"
echo ""
echo "Or use VSCode debugger (F5) with 'FastAPI: Backend' configuration"
