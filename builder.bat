@echo off
chcp 65001 >nul
title Builder

python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

python -c "import sys; print(f'Python {sys.version}')" 2>nul
if errorlevel 1 (
    echo ❌ Python is not working properly
    pause
    exit /b 1
)

echo ✅ Python is installed

set /p "TOKEN=Enter your Discord bot token: "
if "%TOKEN%"=="" (
    echo ❌ No token provided
    pause
    exit /b 1
)

set /p "EXE_NAME=Enter the name for your executable (without .exe): "
if "%EXE_NAME%"=="" (
    set EXE_NAME=DiscordBot
)

set /p "USE_ICON=Do you want to use a custom icon? (y/n): "
if /i "%USE_ICON%"=="y" (
    set /p "ICON_PATH=Enter the path to your .ico file: "
    if exist "%ICON_PATH%" (
        set ICON_OPTION=--icon="%ICON_PATH%"
    ) else (
        echo ❌ Icon file not found: %ICON_PATH%
        set ICON_OPTION=
    )
) else (
    set ICON_OPTION=
)

echo Creating bot file with your token...
(
echo TOKEN = "%TOKEN%"
echo.
) > temp_token.py

copy /b temp_token.py + oney.py bot_with_token.py >nul

echo Installing required packages...
pip install -r requirements.txt

echo Building executable with PyInstaller...
pip install pyinstaller

pyinstaller --onefile --windowed %ICON_OPTION% --name "%EXE_NAME%" bot_with_token.py

if errorlevel 1 (
    echo ❌ Build failed!
    pause
    exit /b 1
)

del temp_token.py
del bot_with_token.py

echo.
echo ================================
echo    BUILD COMPLETE!
echo ================================
echo.
echo ✅ Executable created: dist\%EXE_NAME%.exe
echo.
echo You can now run %EXE_NAME%.exe
echo.

pause
