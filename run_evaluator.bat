@echo off
echo Team Ideas Evaluator
echo =====================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in PATH.
    echo Please install Python 3.8 or higher from https://www.python.org/downloads/
    pause
    exit /b 1
)

echo Checking for required packages...
echo.

REM Install required packages if not already installed
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo.
    echo Error installing required packages.
    pause
    exit /b 1
)

echo.
echo All required packages installed successfully.
echo.

REM Check if .env file exists
if not exist .env (
    echo Warning: .env file not found.
    echo Creating .env file from template...
    copy .env.template .env
    echo.
    echo Please edit the .env file to add your API keys.
    echo Press any key to continue without API keys (mock mode)...
    pause >nul
)

echo.
echo Running idea evaluator...
echo.

REM Run the script
python Team_ideas_rating\idea_evaluator.py

echo.
echo Script execution completed.
echo.
echo Check the Team_ideas_rating folder for the output files:
echo - detailed_ratings.xlsx
echo - summary_ratings.xlsx
echo.

pause