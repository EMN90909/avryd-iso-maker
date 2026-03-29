@echo off
echo 🚀 Starting Avryd GRUB Edition...
echo ⚠️  Please ensure you run this as Administrator for USB access.
echo.

:: Check if venv exists, else create
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

:: Activate and install deps
call venv\Scripts\activate
pip install -r requirements.txt

:: Run the app
python main.py

pause
