@echo off
setlocal enabledelayedexpansion

echo ##########################################
echo # Kabuzan Setup \u0026 Launcher               #
echo ##########################################

REM Check if Python is installed
python --version \u003enul 2\u00261
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Please install Python from https://www.python.org/
    pause
    exit /b 1
)

REM Check for virtual environment
if not exist "venv" (
    echo [INFO] Creating virtual environment...
    python -m venv venv
)

echo [INFO] Activating virtual environment...
call venv\\Scripts\\activate

echo [INFO] Installing/Updating requirements...
python -m pip install --upgrade pip
pip install -r requirements.txt

echo [INFO] Starting the Kabuzan Web App...
echo [INFO] Access the app at http://localhost:8000
python -m uvicorn webapp.main:app --host 127.0.0.1 --port 8000 --reload

pause
