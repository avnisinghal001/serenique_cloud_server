@echo off
echo ========================================
echo Serenique Gemini Server Setup
echo ========================================
echo.

REM Check if virtual environment exists
if exist "venv\" (
    echo Virtual environment already exists.
    set /p recreate="Do you want to recreate it? (y/N): "
    if /i "%recreate%"=="y" (
        echo Removing existing virtual environment...
        rmdir /s /q venv
    ) else (
        echo Using existing virtual environment.
    )
)

REM Create virtual environment if it doesn't exist
if not exist "venv\" (
    echo.
    echo [1/4] Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo Error: Failed to create virtual environment
        echo Make sure Python 3.7+ is installed
        pause
        exit /b 1
    )
    echo √ Virtual environment created
)

REM Activate virtual environment
echo.
echo [2/4] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo Error: Failed to activate virtual environment
    pause
    exit /b 1
)
echo √ Virtual environment activated

REM Install dependencies
echo.
echo [3/4] Installing Python dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo Error: Failed to install dependencies
    pause
    exit /b 1
)
echo √ Dependencies installed

REM Check for .env file and GOOGLE_API_KEY
echo.
echo [4/4] Checking configuration...
if exist ".env" (
    echo √ .env file found
    for /f "tokens=*" %%a in (.env) do set %%a
)

if "%GOOGLE_API_KEY%"=="" (
    echo.
    echo WARNING: GOOGLE_API_KEY not set!
    echo.
    echo To set it, either:
    echo   1. Add to .env file:
    echo      echo GOOGLE_API_KEY=your-api-key-here ^> .env
    echo.
    echo   2. Set in PowerShell:
    echo      $env:GOOGLE_API_KEY="your-api-key-here"
    echo.
) else (
    echo √ GOOGLE_API_KEY is configured
)

echo.
echo ========================================
echo √ Setup complete!
echo ========================================
echo.
echo To activate the virtual environment:
echo   venv\Scripts\activate
echo.
echo To run the server:
echo   uvicorn main:app --reload --port 5001
echo.
echo Or run with the venv directly:
echo   venv\Scripts\python -m uvicorn main:app --reload --port 5001
echo.
echo Then visit:
echo   http://localhost:5001 - Homepage
echo   http://localhost:5001/docs - API Documentation
echo   http://localhost:5001/api/health - Health Check
echo.
echo To deactivate the virtual environment:
echo   deactivate
echo.
pause
