"""
Vercel Serverless Function Entry Point for FastAPI

This file serves as the entry point for Vercel deployment.
It imports the FastAPI app instance from the main module.

According to Vercel's FastAPI documentation, the app must be exported
from one of these locations:
- app.py, index.py, server.py
- src/app.py, src/index.py, src/server.py
- app/app.py, app/index.py, app/server.py

We use api/index.py as the entry point for better organization.
"""

# Import the FastAPI app instance from main.py
from main import app

# Vercel will automatically detect and use this 'app' instance
# No additional ASGI configuration needed
