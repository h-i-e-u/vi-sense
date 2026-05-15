@echo off
echo Starting Vi-Sense...

echo Setting up backend...
cd core
if not exist venv (
    python -m venv venv
)
call venv\Scripts\activate.bat
pip install -r requirements.txt
python init_db.py

echo Starting backend server...
start cmd /k "cd core && call venv\Scripts\activate.bat && python run.py"

echo Setting up frontend...
cd ../client
if not exist node_modules (
    npm install
)

echo Starting frontend server...
start cmd /k "cd client && npm run dev"

echo Vi-Sense is running!
echo Backend: http://localhost:8000
echo Frontend: http://localhost:5173
echo API Docs: http://localhost:8000/docs

pause