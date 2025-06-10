@echo off
echo ========================================================
echo    QR Code Watermarking Tool
echo    Created by Arikal Sayangg
echo ========================================================
echo.

echo Starting QR Code Watermarking Tool...

:: Activate virtual environment
call venv\Scripts\activate

:: Check if virtual environment was activated successfully
if %errorlevel% neq 0 (
    echo [ERROR] Failed to activate virtual environment.
    echo Please run install.bat first to set up the environment.
    pause
    exit /b 1
)

:: Start the application
echo.
echo Starting server on http://localhost:5000
echo.
echo To access the application, open your browser and go to:
echo http://localhost:5000
echo.
echo Press Ctrl+C to stop the server when you're done.
echo ========================================================
echo.

python app.py

pause 
