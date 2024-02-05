#!/usr/bin/env python3
import json
import os
import socket
import subprocess
import sys
import time
from datetime import datetime
import requests
from modules import discord, homeassistant, mail

def backup(modules):
    remote = 'encrypted'

    # Backup information
    data = {
        "source": socket.gethostname(),
        "remote": remote,
        "status": "starting"
    }

    # Notify each of the specified modules
    for module in modules:
        module.send(data)

    start_time = datetime.now()

    command = f"/usr/bin/rclone "

    with open("options.json") as file:
        options = json.load(file)
        command += options["operation"] + " "
        for flag in options["flags"]:
            command += f"--{flag} "
        for argument in options["arguments"]:
            command += f"--{argument} {options['arguments'][argument]} "
        for exclusion in options["exclusions"]:
            command += f"--exclude {exclusion} "

        if options["direction"].lower() == "push":
            try:
                command += options["source_remote"] + ":"
            except KeyError:
                command += ""
            try:
                command += options["source_path"] + " "
            except KeyError:
                command += " "
            try:
                command += options["remote"] + ":"
            except KeyError:
                command += ""
            try:
                command += options["remote_path"]
            except KeyError:
                command += ""
        elif options["direction"].lower() == "pull":
            try:
                command += options["remote"] + ":"
            except KeyError:
                command += ""
            try:
                command += options["remote_path"] + " "
            except KeyError:
                command += " "
            try:
                command += options["source_remote"] + ":"
            except KeyError:
                command += ""
            try:
                command += options["source_path"]
            except KeyError:
                command += ""

    print(command)

    # Run the backup
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    process.wait()

    time.sleep(60)

    end_time = datetime.now()
    total_time = f"{end_time - start_time}"

    # Give a report of the outcome
    data = {
        "source": socket.gethostname(),
        "remote": remote,
        "status": "complete",
        "result": process.returncode,
        "time": total_time
    }

    for module in modules:
        module.send(data)

# Handles the remotes
# Handle remote path
# Handle local
# Handle method (sync, move, copy)
# Direction (push, pull)
def main(args):
    with open("secrets.json") as file:
        secrets = json.load(file)

    modules = []

    if "discord" in secrets:
        webhook = secrets["discord"]["webhook"]
        modules.append(discord.Discord(webhook))
    if "homeassistant" in secrets:
        server = secrets["homeassistant"]["server"]
        api_key = secrets["homeassistant"]["api_key"]
        modules.append(homeassistant.HomeAssistant(api_key, server))
    if "mail" in secrets:
        server = secrets["mail"]["server"]
        port = secrets["mail"]["port"]
        sender = secrets["mail"]["sender"]
        recipients = secrets["mail"]["recipients"]
        username = secrets["mail"]["username"] if secrets["mail"]["username"] else sender
        password = secrets["mail"]["password"]
        protocol = secrets["mail"]["protocol"]
        modules.append(mail.Mail(recipients, sender, username, password, server, port, protocol))

    backup(modules)

if __name__ == "__main__":
    main(sys.argv)