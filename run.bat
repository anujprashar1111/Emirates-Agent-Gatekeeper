@echo off
title Emirates Agent Gatekeeper - MBA Project (PGD202566060)
color 0F
echo =====================================================================
echo       EMIRATES AGENT GATEKEEPER - MBA COLLEGE PROJECT
echo             Student Enrolment No: PGD202566060
echo =====================================================================
echo.

REM Determine Python executable
set "PYTHON_CMD="

REM Check if python is in PATH
python --version >nul 2>&1
if %ERRORLEVEL% equ 0 (
    set "PYTHON_CMD=python"
    goto :FOUND_PYTHON
)

REM Check if py launcher is available
py --version >nul 2>&1
if %ERRORLEVEL% equ 0 (
    set "PYTHON_CMD=py"
    goto :FOUND_PYTHON
)

REM Check codex runtime python
if exist "%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" (
    set "PYTHON_CMD=%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
    goto :FOUND_PYTHON
)

REM Check local AppData python
for /d %%D in ("%LOCALAPPDATA%\Programs\Python\Python*") do (
    if exist "%%D\python.exe" (
        set "PYTHON_CMD=%%D\python.exe"
        goto :FOUND_PYTHON
    )
)

:FOUND_PYTHON
if "%PYTHON_CMD%"=="" (
    echo [ERROR] Python not found on this computer.
    echo Please install Python 3.9+ from https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [INFO] Using Python: %PYTHON_CMD%
echo.
echo [1/2] Verifying dependencies...
"%PYTHON_CMD%" -m pip install -r requirements.txt --quiet
if %ERRORLEVEL% neq 0 (
    echo [WARNING] Could not install all packages with --quiet, attempting standard install...
    "%PYTHON_CMD%" -m pip install -r requirements.txt
)

echo.
echo [2/2] Launching Emirates Agent Gatekeeper Streamlit Dashboard...
echo =====================================================================
echo  If the page does not open automatically, open your browser and visit:
echo  ---> http://127.0.0.1:8501  or  http://localhost:8501
echo =====================================================================
echo (IMPORTANT: Keep this black command window open while using the app!)
echo.

"%PYTHON_CMD%" -m streamlit run app.py --server.address 127.0.0.1 --server.port 8501
pause
