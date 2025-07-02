@echo off
echo Setting up AI Negotiation Platform...

REM Check for Python installation
python --version > nul 2>&1
if errorlevel 1 (
    echo Python is not installed! Please install Python 3.9 or higher.
    pause
    exit /b 1
)

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate

REM Install requirements
echo Installing requirements...
pip install -r negotiation_platform/requirements.txt

REM Create .env file if it doesn't exist
if not exist "negotiation_platform\.env" (
    echo Creating .env file...
    copy negotiation_platform\.env.example negotiation_platform\.env
    echo Please edit the .env file and add your Gemini API key
)

REM Initialize the database
echo Initializing database...
cd negotiation_platform
python -c "from database import init_db; init_db('negotiations.db')"
cd ..

echo Setup completed successfully!
echo To start the application, run: run.bat

pause
