#!/bin/bash

# Quick start script for Serenique Gemini Server

if [ ! -d "venv" ]; then
    echo "Virtual environment not found!"
    echo "Please run ./setup.sh first to create it."
    exit 1
fi

echo "Starting Serenique Gemini Server..."
echo ""

# Activate virtual environment
source venv/bin/activate

# Load .env if exists
if [ -f ".env" ]; then
    source .env
fi

# Check for API key
if [ -z "$GOOGLE_API_KEY" ]; then
    echo "⚠️  WARNING: GOOGLE_API_KEY not set!"
    echo "Server may not work correctly."
    echo ""
fi

# Start server
echo "Server starting at http://localhost:5001"
echo "Press Ctrl+C to stop"
echo ""

venv/bin/python -m uvicorn main:app --reload --port 5001
