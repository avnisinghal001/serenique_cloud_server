#!/bin/bash

echo "========================================"
echo "Serenique Gemini Server Setup"
echo "========================================"
echo ""

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo "Virtual environment already exists."
    read -p "Do you want to recreate it? (y/N): " recreate
    if [[ $recreate =~ ^[Yy]$ ]]; then
        echo "Removing existing virtual environment..."
        rm -rf venv
    else
        echo "Using existing virtual environment."
    fi
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo ""
    echo "[1/4] Creating virtual environment..."
    python -m venv venv
    if [ $? -ne 0 ]; then
        echo "Error: Failed to create virtual environment"
        echo "Make sure Python 3.7+ is installed"
        exit 1
    fi
    echo "✓ Virtual environment created"
fi

# Activate virtual environment
echo ""
echo "[2/4] Activating virtual environment..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "Error: Failed to activate virtual environment"
    exit 1
fi
echo "✓ Virtual environment activated"

# Install dependencies
echo ""
echo "[3/4] Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "Error: Failed to install dependencies"
    exit 1
fi
echo "✓ Dependencies installed"

# Check for .env file and GOOGLE_API_KEY
echo ""
echo "[4/4] Checking configuration..."
if [ -f ".env" ]; then
    echo "✓ .env file found"
    source .env
fi

if [ -z "$GOOGLE_API_KEY" ]; then
    echo ""
    echo "⚠️  WARNING: GOOGLE_API_KEY not set!"
    echo ""
    echo "To set it, either:"
    echo "  1. Add to .env file:"
    echo "     echo 'GOOGLE_API_KEY=your-api-key-here' > .env"
    echo ""
    echo "  2. Export in terminal:"
    echo "     export GOOGLE_API_KEY=\"your-api-key-here\""
    echo ""
else
    echo "✓ GOOGLE_API_KEY is configured"
fi

echo ""
echo "========================================"
echo "✅ Setup complete!"
echo "========================================"
echo ""
echo "To activate the virtual environment:"
echo "  source venv/bin/activate"
echo ""
echo "To run the server:"
echo "  uvicorn main:app --reload --port 5001"
echo ""
echo "Or run with the venv:"
echo "  venv/bin/python -m uvicorn main:app --reload --port 5001"
echo ""
echo "Then visit:"
echo "  http://localhost:5001 - Homepage"
echo "  http://localhost:5001/docs - API Documentation"
echo "  http://localhost:5001/api/health - Health Check"
echo ""
echo "To deactivate the virtual environment:"
echo "  deactivate"
echo ""
