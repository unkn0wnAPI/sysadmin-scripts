#!/usr/bin/python3

#
## Script Name: PostgreSQL Backup Script
## Author:      unkn0wnAPI [https://github.com/unkn0wnAPI]
## Information: Automated script that backs up PostgreSQL databases (for use in a cron job)
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
DATABASES: list[str] = ["your_db1", "your_db2"]  # Set to [] to use pg_dumpall for all DBs
MAX_BACKUPS: int = 7
BACKUP_GLOBALS: bool = True  # Set to True to backup globals, False to skip
PG_HOST: str = "localhost"  # PostgreSQL host, change if needed
PG_USER: str = "postgres"  # PostgreSQL user, change if needed
# The reset MUST BE SET in the .pgpass file for the user running this script

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
                "footer": "PostgreSQL Backup",
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
        notify_slack(f"PostgreSQL backup error: {description} failed on {socket.gethostname()}")
        return False

def gzip_compression(source_path):
    compressed_path = str(source_path) + ".gz"

    with open(source_path, 'rb') as f_in, gzip.open(compressed_path, 'wb') as f_out:
        shutil.copyfileobj(f_in, f_out)
    os.remove(source_path)

    return compressed_path

def rotate_backups(backup_dir, hostname):
    logging.info("Rotating PSQL backups.")
    db_backups = sorted(
        backup_dir.glob(f"{hostname}_*.sql.gz"),
        key=os.path.getmtime,
        reverse=True
    )

    for old_backup in db_backups[MAX_BACKUPS:]:
        try:
            old_backup.unlink()
            logging.info(f"Deleted old DB backup: {old_backup}")
        except Exception as e:
            logging.error(f"Failed to delete old DB backup {old_backup}: {e}")

    if not BACKUP_GLOBALS:
        logging.info("Skipping globals backup rotation as per configuration.")
        return
    else:
        logging.info("Rotating globals backups.")

        globals_backups = sorted(
            backup_dir.glob(f"{hostname}_*_globals.sql.gz"),
            key=os.path.getmtime,
            reverse=True
        )

        for old_backup in globals_backups[MAX_BACKUPS:]:
            try:
                old_backup.unlink()
                logging.info(f"Deleted old globals backup: {old_backup}")
            except Exception as e:
                logging.error(f"Failed to delete old globals backup {old_backup}: {e}")


#
## Script Start point
#
def main():
    hostname = socket.gethostname()
    date_str = datetime.now().strftime('%d-%m-%Y')
    dump_file = BACKUP_DIR / f"{hostname}_{date_str}.sql"
    globals_dump_file = BACKUP_DIR / f"{hostname}_{date_str}_globals.sql"
    os.makedirs(BACKUP_DIR, exist_ok=True)

    # Run pg_isready (no host/port, uses default env and pgpass)
    if not shell_exec(f"pg_isready -h {PG_HOST}", "PostgreSQL readiness check"):
        logging.error("PostgreSQL is not ready. Aborting backup.")
        return 1

    if DATABASES:
        # Dump each database individually and concatenate output to single file
        with open(dump_file, 'wb') as outfile:
            for db in DATABASES:
                logging.info(f"Backing up database: {db}")
                cmd = f"pg_dump -h {PG_HOST} -U {PG_USER} {db}"
                
                try:
                    proc = subprocess.run(cmd, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    outfile.write(proc.stdout)
                    logging.info(f"Finished backup of database {db}")
                except subprocess.CalledProcessError as e:
                    logging.error(f"pg_dump failed for database {db}:\n{e.stderr.decode()}")
                    notify_slack(f"PostgreSQL backup error: pg_dump failed for {db} on {hostname}")
                    return 1
    else:
        # Dump all databases with pg_dumpall
        cmd = f"pg_dumpall -h {PG_HOST} -U {PG_USER} > {dump_file}"
        if not shell_exec(cmd, "pg_dumpall"):
            logging.error("pg_dumpall failed. Aborting backup.")
            return 1

    # Dump globals
    if not BACKUP_GLOBALS:
        logging.info("Skipping globals backup as per configuration.")
        globals_dump_file = None
    else:
        logging.info("Backing up PostgreSQL globals.")

        globals_cmd = f"pg_dumpall -h {PG_HOST} -U {PG_USER} --globals-only > {globals_dump_file}"
        if not shell_exec(globals_cmd, "pg_dumpall --globals-only"):
            logging.error("Globals backup failed. Aborting backup.")
            return 1

    # Check if the dump files exist and are not empty
    if not dump_file.exists() or dump_file.stat().st_size == 0:
        logging.error("Backup file is empty or missing.")
        notify_slack(f"PostgreSQL backup failed: SQL backup is empty or missing on {hostname}")
        return 1

    # Check if the globals dump file exists and is not empty (only if BACKUP_GLOBALS is enabled)
    if BACKUP_GLOBALS and (not globals_dump_file.exists() or globals_dump_file.stat().st_size == 0):
        logging.error("Globals backup file is empty or missing.")
        notify_slack(f"PostgreSQL backup failed: SQL Globals backup is empty or missing on {hostname}")
        return 1

    # Compress the backup
    compressed_path = gzip_compression(dump_file)
    logging.info(f"Compressed backup to: {compressed_path}")

    # Compress globals dump
    compressed_globals_path = gzip_compression(globals_dump_file)
    logging.info(f"Compressed globals backup to: {compressed_globals_path}")

    # Rotate backups
    rotate_backups(BACKUP_DIR, hostname)
    logging.info("Backup rotation completed successfully.")

    logging.info("Backup process completed successfully.")

if __name__ == '__main__':
    main()
