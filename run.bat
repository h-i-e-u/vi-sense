@echo off
setlocal

set "ROOT_DIR=%~dp0"
set "CORE_DIR=%ROOT_DIR%core"
set "CLIENT_DIR=%ROOT_DIR%client"

echo Starting Vi-Sense...

echo Setting up backend...
cd /d "%CORE_DIR%"
if not exist venv (
    python -m venv venv
)
call venv\Scripts\activate.bat
pip install -r requirements.txt
python init_db.py

echo Starting backend server...
start "Vi-Sense Backend" cmd /k ""cd /d "%CORE_DIR%" && call venv\Scripts\activate.bat && python run.py""

echo Setting up frontend...
cd /d "%CLIENT_DIR%"
if not exist node_modules (
    npm install
)

echo Starting frontend server...
start "Vi-Sense Frontend" cmd /k ""cd /d "%CLIENT_DIR%" && npm run dev""

echo Vi-Sense is running!
echo Backend: http://localhost:8000
echo Frontend: http://localhost:5173
echo API Docs: http://localhost:8000/docs

pause
