@echo off
setlocal enabledelayedexpansion

echo HALO Portfolio Simulator Installation and Setup
echo ===============================================
echo.
echo This script will set up everything needed to run the Portfolio Simulator.
echo.
echo Step 1: Checking if Python is installed...

python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed. The script will download and install it for you.
    echo.
    
    echo Creating temporary directory...
    mkdir temp_python_installer 2>nul
    cd temp_python_installer
    
    echo Downloading Python installer...
    powershell -Command "& {Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.7/python-3.11.7-amd64.exe' -OutFile 'python_installer.exe'}"
    
    if not exist python_installer.exe (
        echo Failed to download Python installer.
        echo Please install Python manually from https://www.python.org/downloads/
        echo Be sure to check "Add Python to PATH" during installation.
        pause
        cd ..
        exit /b 1
    )
    
    echo Installing Python... (This may take a few minutes)
    echo Please accept any security prompts that appear.
    python_installer.exe /quiet InstallAllUsers=1 PrependPath=1
    
    if %errorlevel% neq 0 (
        echo Failed to install Python.
        echo Please try installing Python manually from https://www.python.org/downloads/
        pause
        cd ..
        exit /b 1
    )
    
    echo Python installation completed!
    cd ..
    
    echo Refreshing environment variables...
    call RefreshEnv.cmd 2>nul || (
        echo Setting PATH manually...
        set PATH=C:\Program Files\Python311;C:\Program Files\Python311\Scripts;%PATH%
    )
    
    echo.
    echo Python has been installed! Continuing setup...
) else (
    echo Python is already installed! Continuing setup...
)

echo.
echo Step 2: Setting up virtual environment...

if not exist .venv (
    python -m venv .venv
    if %errorlevel% neq 0 (
        echo Failed to create virtual environment.
        echo Please contact the person who shared this with you.
        pause
        exit /b
    )
)

echo Step 3: Activating virtual environment...
call .venv\Scripts\activate.bat

echo Step 4: Installing required packages...
echo This may take a few minutes...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Failed to install required packages.
    echo Please contact the person who shared this with you.
    pause
    exit /b
)

echo.
echo All setup completed successfully!
echo.
echo Starting HALO Portfolio Simulator...
echo.
echo (When you're done using the simulator, you can close its window.)

python gui.py

echo.
echo Thank you for using HALO Portfolio Simulator!
echo To run it again, just double-click this file.
echo.
pause 