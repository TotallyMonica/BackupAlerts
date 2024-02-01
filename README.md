# Backup Alerts

## A simple wrapper script for rclone to alert about backups

If you have a better name for this, feel free to open an issue with the name.

------------

## Requirements

System packages:
python3
rclone

Python packages:
requests

## Installation

On Debian/Ubuntu based systems:
```bash
sudo apt update
sudo apt install python3 python3-pip rclone git
pip install requests
git clone https://github.com/TotallyMonica/BackupAlerts
chmod +x BackupAlerts/main.py
```

On RedHat/Fedora based systems:
```bash
sudo dnf install python3 python3-pip rclone git
pip install requests
git clone https://github.com/TotallyMonica/BackupAlerts
chmod +x BackupAlerts/main.py
```

Please note: this script has been untested on non-Linux based operating systems. Use at your own risk for non-Linux environments

## Configuration

Prior to running, it is important that you configure the script correctly. Namely, there are two files you will want to create in the working folder of the script: options.json and secrets.json. Template scripts are provided in the repo or can be copied from the README

Template options.json:

```json
{
  "operation": "",
  "direction": "",
  "remote": "",
  "source_path":  "",
  "flags": [""],
  "arguments": {
  },
  "exclusions": [""]
}
```

Template secrets.json
```
{
  "discord": {
    "webhook": ""
  },
  "homeassistant": {
    "server": "",
    "api_key": ""
  },
  "mail": {
    "sender": "",
    "recipients": ["", ""],
    "server": "",
    "port": 587,
    "protocol": "",
    "username": "",
    "password": ""
  }
}
```

## Usage:
```bash
cd /path/to/script
./main.py
```

## To-Do:
- [ ] Add in Slack support
- [ ] Test on Windows
- [ ] Add in inclusion support
- [ ] Mail integration: add in support for SSL/TLS
- [ ] Better module detection and importing
- [ ] Better error handling

Stretch goals include:
- [ ] Configurable output for alerts
- [ ] Show size of backup in alerts
- [ ] Show amount of files backed up in alerts

## Purpose
I use rclone to back up my computer to a Backblaze B2 bucket, but I was unsure if backups were being triggered or if they were successful. As such, I created this to send me notifications through a Discord webhook. After doing some more research, it was not that difficult to add in support for Home Assistant alerts. It further served as an opportunity for me to learn about sending emails from a script, which is where I receive most of my alerts to begin with.
