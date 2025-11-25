@echo off
REM Smart Aquarium Setup Script for Windows

echo ================================
echo Smart Aquarium Setup
echo ================================

REM Check Python installation
echo.
echo [1/4] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo OK - %PYTHON_VERSION% found

REM Install dependencies
echo.
echo [2/4] Installing Python packages...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install packages
    pause
    exit /b 1
)
echo OK - Packages installed successfully

REM Database migrations
echo.
echo [3/4] Running database migrations...
python manage.py migrate
if errorlevel 1 (
    echo ERROR: Migration failed
    pause
    exit /b 1
)
echo OK - Migrations completed

REM Collect static files
echo.
echo [4/4] Collecting static files...
python manage.py collectstatic --noinput
if errorlevel 1 (
    echo ERROR: Static files collection failed
    pause
    exit /b 1
)
echo OK - Static files collected

echo.
echo ================================
echo Setup Complete!
echo ================================
echo.
echo Next steps:
echo 1. Update MySQL credentials in smartAquarium\settings.py
echo 2. Update API key in api\views.py
echo 3. Run: python manage.py runserver
echo 4. Visit: http://localhost:8000
echo.
echo Create superuser by running:
echo python manage.py createsuperuser
echo.
pause
