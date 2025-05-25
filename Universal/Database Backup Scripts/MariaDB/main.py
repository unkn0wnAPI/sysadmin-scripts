#!/usr/bin/python3

#
## Script Name: MariaDB Backup Script
## Author:      unkn0wnAPI [https://github.com/unkn0wnAPI]
## Information: Automated script that backs up MariaDB databases (for use in a cron job)
#

#
## Imports
#
from datetime import datetime
from pathlib import Path
import subprocess
import requests
import logging
import socket
import shutil
import gzip
import os

#
## Init configuration variable
#
BACKUP_DIR: Path = Path("/mnt/your_backup_directory")
LOG_DIR: Path = BACKUP_DIR / "logs"
SLACK_WEBHOOK: str = "https://hooks.slack.com/services/your/webhook/url"
DATABASES: list[str] = ["your_db1", "your_db2"]  # Set to [] to use --all-databases
MAX_BACKUPS: int = 7
# The connection settings MUST BE SET in the .my.cnf file for the user running this script

#
## Core Logging Setup
#
os.makedirs(LOG_DIR, exist_ok=True)
logging.basicConfig(
    filename=LOG_DIR / f'backup_{datetime.now().strftime("%Y-%m-%d")}.log',
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
                "footer": "MariaDB Backup",
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
        notify_slack(f"MariaDB backup error: {description} failed on {socket.gethostname()}")

        return False

def gzip_compression(source_path):
    compressed_path = str(source_path) + ".gz"

    with open(source_path, 'rb') as f_in, gzip.open(compressed_path, 'wb') as f_out:
        shutil.copyfileobj(f_in, f_out)
    os.remove(source_path)

    return compressed_path

def rotate_backups(backup_dir, hostname):
    backups = sorted(backup_dir.glob(f"{hostname}_*.sql.gz"), key=os.path.getmtime, reverse=True)

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
    dump_file = BACKUP_DIR / f"{hostname}_{date_str}.sql"
    os.makedirs(BACKUP_DIR, exist_ok=True)

    # Run mariadb-check
    check_cmd = "mariadb-check --defaults-file=~/.my.cnf --all-databases"
    if not shell_exec(check_cmd, "mariadb-check"):
        logging.error("MariaDB check failed. Aborting backup.")
        return 1

    # Build mariadb-dump command
    if DATABASES:
        dbs = ' '.join(DATABASES)
        dump_cmd = f"mariadb-dump --defaults-file=~/.my.cnf --skip-ssl --single-transaction " \
                   f"--flush-logs --events --routines --databases {dbs} > {dump_file}"
    else:
        dump_cmd = f"mariadb-dump --defaults-file=~/.my.cnf --skip-ssl --single-transaction " \
                   f"--flush-logs --events --routines --all-databases > {dump_file}"

    if not shell_exec(dump_cmd, "mariadb-dump"):
        logging.error("MariaDB dump failed. Aborting backup.")
        return 1

    if not dump_file.exists() or dump_file.stat().st_size == 0:
        logging.error("Backup file is empty or missing.")
        notify_slack(f"MariaDB backup failed: SQL Backup is empty or missing {hostname}")
        return 1

    # Compress the backup
    compressed_path = gzip_compression(dump_file)
    logging.info(f"Compressed backup to: {compressed_path}")

    # Rotate backups
    rotate_backups(BACKUP_DIR, hostname)
    logging.info("Backup rotation completed successfully.")

    logging.info("Backup process completed successfully.")

if __name__ == '__main__':
    main()
