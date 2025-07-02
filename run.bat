@echo off
echo Starting AI Negotiation Platform...

REM Check if virtual environment exists
if not exist "venv" (
    echo Virtual environment not found. Running setup first...
    call setup.bat
)

REM Activate virtual environment
call venv\Scripts\activate

REM Run the application
cd negotiation_platform
python app.py

REM Keep the window open if there's an error
if errorlevel 1 pause
