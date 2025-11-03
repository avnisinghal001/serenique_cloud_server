@echo off

REM Quick start script for Serenique Gemini Server

if not exist "venv\" (
    echo Virtual environment not found!
    echo Please run setup.bat first to create it.
    pause
    exit /b 1
)

echo Starting Serenique Gemini Server...
echo.

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Load .env if exists
if exist ".env" (
    for /f "tokens=*" %%a in (.env) do set %%a
)

REM Check for API key
if "%GOOGLE_API_KEY%"=="" (
    echo WARNING: GOOGLE_API_KEY not set!
    echo Server may not work correctly.
    echo.
)

REM Start server
echo Server starting at http://localhost:5001
echo Press Ctrl+C to stop
echo.

venv\Scripts\python -m uvicorn main:app --reload --port 5001
