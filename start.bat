@echo off
cd /d "%~dp0"
if not exist .venv py -3 -m venv .venv
.venv\Scripts\python.exe -c "import pypdf" 2>nul || .venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe app.py --open
pause
