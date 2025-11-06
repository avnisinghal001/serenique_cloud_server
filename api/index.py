"""
Vercel Serverless Function Entry Point for FastAPI

This file serves as the entry point for Vercel deployment.
It imports the FastAPI app instance from the main module.

Vercel will automatically detect and serve the FastAPI app.
"""

import sys
import os

# Add parent directory to path to import main.py from root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the FastAPI app instance from main.py in root
from main import app

# Vercel will automatically detect and use this 'app' instance
# No additional ASGI configuration needed
