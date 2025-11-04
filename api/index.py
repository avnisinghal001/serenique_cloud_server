"""
Vercel Serverless Function Entry Point for Serenique API

This file is the ASGI handler that Vercel uses to run the FastAPI app.
All routes from main.py are exposed through this entry point.
"""

from main import app

# Vercel expects an 'app' or 'handler' export
# FastAPI app is already an ASGI application, so we just export it
handler = app

# For compatibility with different Vercel configurations
application = app
