#!/usr/bin/python3

#
## Script Name: System Configuration Backup Script
## Author:      unkn0wnAPI [https://github.com/unkn0wnAPI]
## Information: Automated script that backs up Linux directories (for use in a cron job)
#

#
## Imports
#
from datetime import datetime
from pathlib import Path
import subprocess
import logging
import socket
import requests
import os

#
## Init configuration variable
#
BACKUP_DIR = Path("/mnt/your_backup_directory")
LOG_DIR = BACKUP_DIR / "logs"
LOG_FILE_PREFIX = "backup"
SLACK_WEBHOOK = "https://hooks.slack.com/services/your/webhook/url"
MAX_BACKUPS = 7
INCLUDE_PATHS = ["/dir1", "/dir2"] # Directories to include [absolute paths]
EXCLUDE_PATHS = ["/dir1/exclude", "/dir2/exclude"]  # Directories to exclude [absolute paths]

#
## Core Logging Setup
#
os.makedirs(LOG_DIR, exist_ok=True)
logging.basicConfig(
    filename=LOG_DIR / f'{LOG_FILE_PREFIX}_{datetime.now().strftime("%Y-%m-%d")}.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

#
## Core Functions
#
def notify_slack(message):
    payload = {
        "text": "<!channel>",
        "attachments": [
            {
                "color": '#FF0000',
                "text": message,
                "footer": "System Backup",
                "ts": int(datetime.now().timestamp())
            }
        ]
    }
    try:
        requests.post(SLACK_WEBHOOK, json=payload)
    except Exception as e:
        logging.error(f"Slack notification failed: {e}")

def shell_exec(command, description):
    logging.info(f"Running: {description}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True)
        logging.info(result.stdout.decode())
        return True
    except subprocess.CalledProcessError as e:
        logging.error(f"{description} failed:\n{e.stderr.decode()}")
        notify_slack(f"System backup error: {description} failed on {socket.gethostname()}")
        return False

def rotate_backups(backup_dir, hostname):
    backups = sorted(
        backup_dir.glob(f"{hostname}-*.tgz"),
        key=os.path.getmtime,
        reverse=True
    )

    for old_backup in backups[MAX_BACKUPS:]:
        try:
            old_backup.unlink()
            logging.info(f"Deleted old backup: {old_backup}")
        except Exception as e:
            logging.error(f"Failed to delete old backup {old_backup}: {e}")

#
## Script Start point
#
def main():
    hostname = socket.gethostname()
    date_str = datetime.now().strftime('%d-%m-%Y')
    backup_file = BACKUP_DIR / f"{hostname}-{date_str}.tgz"

    os.makedirs(BACKUP_DIR, exist_ok=True)

    # Build tar command with exclusions
    exclude_args = " ".join([f"--exclude='{path}'" for path in EXCLUDE_PATHS])
    tar_command = f"tar -zcpvf {backup_file} {exclude_args} {' '.join(INCLUDE_PATHS)}"

    if not shell_exec(tar_command, "Docker data tar backup"):
        return 1

    # Check backup file
    if not backup_file.exists() or backup_file.stat().st_size == 0:
        logging.error("Backup file is empty or missing.")
        notify_slack(f"Docker backup failed: Archive is empty or missing on {hostname}")
        return 1

    # Rotate old backups
    rotate_backups(BACKUP_DIR, hostname)
    logging.info("Backup rotation completed successfully.")
    logging.info("Docker backup completed successfully.")

if __name__ == "__main__":
    main()