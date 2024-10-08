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
from enum import Enum

class ErrorCode(Enum):
    SUCCESS = 0
    SYNTAX_USAGE_ERROR = 1
    NOT_OTHERWISE_CATEGORISED = 2
    DIRECTORY_NOT_FOUND = 3
    FILE_NOT_FOUND = 4
    TEMPORARY_ERROR = 5
    LESS_SERIOUS_ERROR = 6
    FATAL_ERROR = 7
    TRANSFER_EXCEEDED = 8
    NO_FILES_TRANSFERRED = 9
    DURATION_EXCEEDED = 10

CWD = os.path.dirname(os.path.realpath(__file__)) + "/"

def friendly_size(size):
    units = {
        '0': 'B',
        '1': 'KB',
        '2': 'MB',
        '3': 'GB',
        '4': 'TB',
        '5': 'PB'
    }

    unit = 0

    while size > 1024 and unit < 5:
        unit += 1
        size = size / 1024

    return f"{round(size, 2)} {units[f'{unit}']}"

def calculate_size(remote):
    # Build remote information
    with open(CWD + "options.json") as file:
        options = json.load(file)
        source = ""
        dest = ""
        if "source_remote" in options:
            source += options["source_remote"] + ":"
        if "source_path" in options:
            source += options["source_path"]
        if "remote" in options:
            dest += remote + ":"
        if "remote_path" in options:
            dest += options["remote_path"]

    # Run the check and format the diff
    command = f"rclone check {source} {dest} --combined -"
    process = subprocess.run(command.split(" "), capture_output=True)
    diffs = process.stdout.decode().strip().split("\n")

    files_to_backup = []
    for diff in diffs:
        diff = diff.split(" ")
        # Ignore matches or files only the destination has
        if diff[0] == '-' or diff[0] == '=':
            pass
        else:
            file = " ".join(diff[1:])
            file_stats = os.stat("D:/" + file)
            files_to_backup.append([file, file_stats.st_size])

    return files_to_backup

def backup(modules, options, remote, required=[]):
    # diff = calculate_size(remote)
    # if len(diff) == 0:
    #     data = {
    #         "source": socket.gethostname(),
    #         "remote": remote,
    #         "status": "cancel"
    #     }
    # else:
    #     # Backup information
    data = {
        "source": socket.gethostname(),
        "remote": remote,
        "status": "starting",
        # "count": len(diff),
        # "size": sum(size[1] for size in diff)
    }

    # Notify each of the specified modules
    failed_modules = []
    for module in modules:
        if module.notify_level >> 2 & 1:    # Bitwise should be 100 minimum
            try:
                module.send(data)
            except Exception as e:
                if module in required:
                    raise Exception(f"Error sending alert to required module {module.name}")
                print(f"Warning: module {module.name} failed when pushing alert")
                failed_modules.append({
                    "module": module.name,
                    "exception": e.__class__.__name__
                })

    start_time = datetime.now()

    command = f"/usr/bin/rclone "

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
            command += remote + ":"
        except KeyError:
            command += ""
        try:
            command += options["remote_path"]
        except KeyError:
            command += ""
    elif options["direction"].lower() == "pull":
        try:
            command += remote + ":"
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
        "time": total_time,
        # "count": len(diff),
        # "size": sum(size[1] for size in diff)
    }

    # If we have any failed modules add them to the report
    if len(failed_modules) > 0:
        data["failed_modules"] = []
        for failed_module in failed_modules:
            data["failed_modules"].append({
                "name": failed_module.name
            })

    for module in modules:
        if (module.notify_level >> 2 & 1 and process.returncode == 0) \
            or (module.notify_level & 1 and not process.returncode == 0):   # Successful bitwise: 010, failure: 001
            try:
                module.send(data)
            except Exception as e:
                if module in required:
                    raise Exception(f"Error sending alert to required module {module.name}")
                print(f"Warning: module {module.name} failed when pushing alert")
                failed_modules.append({
                    "module": module.name,
                    "exception": e.__class__.__name__
                })

# Handles the remotes
# Handle remote path
# Handle local
# Handle method (sync, move, copy)
# Direction (push, pull)
def main(args):
    if "--no-notify" in args:
        secrets = {}
    else:
        with open(CWD + "secrets.json") as file:
            secrets = json.load(file)

    with open(CWD + "options.json") as file:
        options = json.load(file)

    modules = []
    required_modules = []

    if "discord" in secrets:
        discord_secrets = secrets["discord"]
        modules.append(discord.Discord(discord_secrets["webhook"], discord_secrets["notify_level"]))
        if "required" in discord_secrets and discord_secrets["required"]:
            required_modules.append(modules[-1])
    if "homeassistant" in secrets:
        homeassistant_secrets = secrets["homeassistant"]
        server = homeassistant_secrets["server"]
        api_key = homeassistant_secrets["api_key"]
        notify_level = homeassistant_secrets["notify_level"]
        modules.append(homeassistant.HomeAssistant(api_key, server, notify_level))
        if "required" in homeassistant_secrets and homeassistant_secrets["required"]:
            required_modules.append(modules[-1])
    if "mail" in secrets:
        mail_secrets = secrets["mail"]
        server = mail_secrets["server"]
        port = mail_secrets["port"]
        sender = mail_secrets["sender"]
        recipients = mail_secrets["recipients"]
        username = mail_secrets["username"] if mail_secrets["username"] else sender
        password = mail_secrets["password"]
        protocol = mail_secrets["protocol"]
        notify_level = mail_secrets["notify_level"]
        if "required" in mail_secrets and mail_secrets["required"]:
            required_modules.append(modules[-1])
        modules.append(mail.Mail(recipients, sender, username, password, server, port, protocol, notify_level=notify_level))

    if type(options['remote']) == list:
        for remote in options['remote']:
            backup(modules, options, remote, required_modules)
    else:
        backup(modules, options, options['remote'], required_modules)

if __name__ == "__main__":
    main(sys.argv)
