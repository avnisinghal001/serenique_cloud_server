# Serenique Server - Virtual Environment Setup Guide

## 🚀 Quick Start

### For Linux/Mac/Git Bash:
```bash
# 1. Run setup script
chmod +x setup.sh
./setup.sh

# 2. Start the server
./run.sh
```

### For Windows:
```batch
# 1. Run setup script
setup.bat

# 2. Start the server
run.bat
```

## 📋 What the Setup Does

The `setup.sh` / `setup.bat` scripts will:

1. **Create Virtual Environment** (`venv/` directory)
   - Isolated Python environment
   - Prevents conflicts with system Python packages

2. **Activate Virtual Environment**
   - Linux/Mac: `source venv/bin/activate`
   - Windows: `venv\Scripts\activate`

3. **Install Dependencies**
   - Upgrades pip to latest version
   - Installs all packages from `requirements.txt`
   - Includes: FastAPI, LangChain, Gemini, Firebase

4. **Check Configuration**
   - Verifies `.env` file exists
   - Checks if `GOOGLE_API_KEY` is set
   - Provides setup instructions if missing

## 🔧 Manual Setup (Alternative)

If you prefer to set up manually:

### Linux/Mac/Git Bash:
```bash
# Create virtual environment
python -m venv venv

# Activate it
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Run server
uvicorn main:app --reload --port 5001
```

### Windows PowerShell:
```powershell
# Create virtual environment
python -m venv venv

# Activate it
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Run server
uvicorn main:app --reload --port 5001
```

### Windows CMD:
```batch
# Create virtual environment
python -m venv venv

# Activate it
venv\Scripts\activate.bat

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Run server
uvicorn main:app --reload --port 5001
```

## 📁 Directory Structure After Setup

```
serenique_cloud_server/
├── venv/                    # Virtual environment (created by setup)
│   ├── bin/                # Linux/Mac executables
│   ├── Scripts/            # Windows executables
│   ├── Lib/                # Installed packages
│   └── ...
├── main.py                 # FastAPI application
├── langchain_persona_architect.py
├── firebase_service.py
├── requirements.txt
├── .env                    # Environment variables
├── credentials.json        # Firebase credentials
├── setup.sh               # Linux/Mac setup script
├── setup.bat              # Windows setup script
├── run.sh                 # Linux/Mac quick start
└── run.bat                # Windows quick start
```

## 🎯 Working with Virtual Environment

### Activating the Virtual Environment

**Linux/Mac/Git Bash:**
```bash
source venv/bin/activate
```

**Windows PowerShell:**
```powershell
.\venv\Scripts\Activate.ps1
```

**Windows CMD:**
```batch
venv\Scripts\activate.bat
```

You'll see `(venv)` appear in your terminal prompt when activated.

### Deactivating the Virtual Environment

Simply run:
```bash
deactivate
```

### Installing New Packages

Always activate the virtual environment first, then:
```bash
pip install package-name
```

To save to requirements.txt:
```bash
pip freeze > requirements.txt
```

## 🔄 Updating Dependencies

```bash
# Activate venv first
source venv/bin/activate  # or appropriate command for your OS

# Update specific package
pip install --upgrade package-name

# Update all packages
pip install --upgrade -r requirements.txt

# Save updated versions
pip freeze > requirements.txt
```

## 🗑️ Removing Virtual Environment

If you need to start fresh:

**Linux/Mac:**
```bash
rm -rf venv
./setup.sh  # Run setup again
```

**Windows:**
```batch
rmdir /s venv
setup.bat   # Run setup again
```

## ✅ Verifying Setup

After running setup, verify everything works:

1. **Check Python version:**
   ```bash
   venv/bin/python --version  # Linux/Mac
   venv\Scripts\python --version  # Windows
   ```

2. **Check installed packages:**
   ```bash
   venv/bin/pip list  # Linux/Mac
   venv\Scripts\pip list  # Windows
   ```

3. **Test server:**
   ```bash
   ./run.sh  # Linux/Mac
   run.bat   # Windows
   ```

4. **Visit health check:**
   Open browser to http://localhost:5001/api/health

## 🐛 Troubleshooting

### "python: command not found"
- Install Python 3.7 or higher
- Windows: Add Python to PATH during installation

### "Permission denied" (Linux/Mac)
```bash
chmod +x setup.sh run.sh
```

### "Execution policy" error (Windows PowerShell)
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### "ModuleNotFoundError" when running server
- Make sure virtual environment is activated
- Run setup again: `./setup.sh` or `setup.bat`

### Virtual environment not activating
- Delete venv folder and run setup again
- Check Python installation

## 🎉 Benefits of Virtual Environment

✅ **Isolation**: Packages don't interfere with system Python  
✅ **Reproducibility**: Same environment across machines  
✅ **Clean**: Easy to delete and recreate  
✅ **Version Control**: Pin specific package versions  
✅ **Safety**: No risk to system Python installation  

## 📚 Additional Resources

- [Python venv documentation](https://docs.python.org/3/library/venv.html)
- [FastAPI documentation](https://fastapi.tiangolo.com/)
- [Gemini API documentation](https://ai.google.dev/docs)
- [LangChain documentation](https://python.langchain.com/)
