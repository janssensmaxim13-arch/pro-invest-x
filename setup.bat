@echo off
echo ============================================
echo    ProInvestiX - Automatische Setup
echo ============================================
echo.

:: Vaste locatie voor venv (blijft behouden bij updates)
set VENV_PATH=C:\venvs\proinvestix

:: Check of Python geinstalleerd is
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is niet geinstalleerd!
    echo Download Python van: https://www.python.org/downloads/
    pause
    exit /b 1
)

:: Maak venvs folder als die niet bestaat
if not exist "C:\venvs" (
    echo [INFO] Maak C:\venvs folder aan...
    mkdir C:\venvs
)

:: Maak venv als die niet bestaat
if not exist "%VENV_PATH%" (
    echo [1/3] Virtual environment aanmaken op %VENV_PATH%...
    python -m venv %VENV_PATH%
    echo      Done!
    
    :: Activeer en installeer packages (alleen eerste keer)
    echo [2/3] Virtual environment activeren...
    call %VENV_PATH%\Scripts\activate.bat
    
    echo [3/3] Packages installeren (eenmalig)...
    pip install -r requirements.txt --quiet
) else (
    echo [1/3] Virtual environment bestaat al op %VENV_PATH%
    echo [2/3] Virtual environment activeren...
    call %VENV_PATH%\Scripts\activate.bat
    echo [3/3] Packages al geinstalleerd - skip
)

echo.
echo ============================================
echo    Setup compleet! App wordt gestart...
echo ============================================
echo.

:: Start de app
streamlit run app.py
