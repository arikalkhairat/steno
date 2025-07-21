@echo off
echo ========================================================
echo    QR Code Watermarking Tool - Installer
echo    Created by Arikal Khairat
echo ========================================================
echo.

:: Check if Python is installed
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Please install Python 3.8 or higher from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

:: Check Python version
python -c "import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)" > nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] Python version is older than 3.8
    echo Some features may not work correctly. We recommend updating Python.
    echo.
    choice /C YN /M "Continue anyway?"
    if %errorlevel% equ 2 exit /b 1
    echo.
)

echo [1/5] Creating virtual environment...
if exist venv (
    echo Virtual environment already exists. Skipping creation.
) else (
    python -m venv venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
)

echo [2/5] Activating virtual environment...
call venv\Scripts\activate
if %errorlevel% neq 0 (
    echo [ERROR] Failed to activate virtual environment.
    pause
    exit /b 1
)

echo [3/5] Upgrading pip...
python -m pip install --upgrade pip
if %errorlevel% neq 0 (
    echo [WARNING] Failed to upgrade pip. Continuing with installation...
)

echo [4/5] Installing required packages...
pip install flask python-docx pillow qrcode numpy
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install required packages.
    pause
    exit /b 1
)

echo [5/5] Creating required directories...
if not exist "static" mkdir static
if not exist "static\generated" mkdir static\generated
if not exist "static\img" mkdir static\img
if not exist "uploads" mkdir uploads

echo.
echo ========================================================
echo Installation completed successfully!
echo.
echo To start the application:
echo 1. Run "run.bat" 
echo 2. Open your browser and go to http://localhost:5000
echo ========================================================
echo.

:: Create run.bat file for easy launching
echo @echo off > run.bat
echo echo Starting QR Code Watermarking Tool... >> run.bat
echo call venv\Scripts\activate >> run.bat
echo python app.py >> run.bat
echo pause >> run.bat

echo Run script created: run.bat

pause 
