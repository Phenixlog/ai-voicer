#!/bin/bash
# Setup script for Théoria SaaS

set -e

echo "🎙️  Setting up Théoria SaaS..."

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $python_version"

# Create virtual environment if not exists
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Check PostgreSQL
if command -v psql &> /dev/null; then
    echo "✓ PostgreSQL found"
    
    # Create database if not exists
    if ! psql -lqt | cut -d \| -f 1 | grep -qw theoria; then
        echo "Creating database 'theoria'..."
        createdb theoria || echo "Note: Could not create database automatically"
    else
        echo "✓ Database 'theoria' already exists"
    fi
else
    echo "⚠️  PostgreSQL not found. Please install it:"
    echo "   brew install postgresql@14"
    echo "   brew services start postgresql@14"
    echo "   createdb theoria"
fi

# Create .env if not exists
if [ ! -f ".env" ]; then
    echo "📝 Creating .env from template..."
    cp .env.saas.example .env
    echo "⚠️  Please edit .env and add your API keys:"
    echo "   - MISTRAL_API_KEY"
    echo "   - JWT_SECRET (run: openssl rand -base64 32)"
    echo "   - STRIPE_SECRET_KEY (optional for now)"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env with your API keys"
echo "2. Start the API: python run_saas_api.py"
echo "3. In another terminal:"
echo "   python run_saas_daemon.py login your@email.com"
echo "   python run_saas_daemon.py run"
echo ""
