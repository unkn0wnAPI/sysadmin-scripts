# Database Backup Scripts

This directory contains a collection of scripts designed for specific database engines, optimized for automated backup via cron jobs. Each script set is tailored to the requirements of its target database system.

Currently supported databases:

* MariaDB
* PostgreSQL

## Getting Started

The scripts requires specific packages (See [Prerequisites](#prerequisites) for more information).

### Prerequisites

This tool uses builtin [Python 3](https://www.python.org/) packages:

* subprocess
* requests
* os
* logging
* socket
* gzip
* shutil
* datetime
* Path

## Configuration

Each database backup script can be configured using the following variables:

| Variable        | Variable Type | Description                                                                              | Is Required            |
|-----------------|---------------|------------------------------------------------------------------------------------------|------------------------|
| `BACKUP_DIR`    | `Path`        | Sets the root directory for backups and logs                                             | Yes                    |
| `LOG_DIR`       | `Path`        | Sets the logs directory name (automatically populated if not specified)                  | No (Auto Populated)    |
| `SLACK_WEBHOOK` | `str`         | Slack WebHook URL for error notifications                                                | No (Works w/o it)      |
| `DATABASES`     | `list[str]`   | Specifies which databases to back up (defaults to all databases if empty)                | No                     |
| `MAX_BACKUPS`   | `int`         | Maximum number of backup files to retain                                                 | Yes                    |

### `MariaDB` Specific Configuration

The MariaDB backup script requires you to configure connection settings using a `.my.cnf` file for authentication.

#### `.my.cnf` Creation Guide

```shell
touch $HOME/.my.cnf;

echo "[client]
host=<mariadb_ip>
port=<mariadb_port>

[mariadb-dump]
user=<backup_username>
password=<backup_password>

[mariadb-check]
user=<backup_username>
password=<backup_password>" > ~/.my.cnf;

chmod 600 $HOME/.my.cnf;
```

## PostgreSQL Specific Configuration

The PostgreSQL backup script requires you to configure connection settings using script variables and a `.pgpass` file for authentication.

| Variable  | Variable Type | Description                                              | Is Required    |
|-----------|---------------|----------------------------------------------------------|----------------|
| `PG_HOST` | `str`         | Sets the PostgreSQL server IP                            | Yes            |
| `PG_USER` | `str`         | Sets the PostgreSQL user used to connect to the database | Yes            |

#### `.pgpass` Creation Guide

```shell
touch $HOME/.pgpass;

echo "<pg_ip_address>:<pg_port_address>:*:<pg_username>:<pg_user_password>" > $HOME/.pgpass;

chmod 600 $HOME/.pgpass;
```

## Usage

To run this script you need to issue the following commands:

```properties
./path/to/database_type/main.py
# or
python3 /path/to/database_type/main.py
```
