# Database Backup Scripts

This directory contains a collection of scripts designed for specific database engines, optimized for automated backup via cron jobs. Each script set is tailored to the requirements of its target database system.

Currently supported databases:

* MariaDB
* PostgreSQL

## Getting Started

The scripts requires specific packages (See [Prerequisites](#prerequisites) for more information).

### Prerequisites

This tool uses [GNU TAR](https://www.gnu.org/software/tar/) for compression, [Python 3](https://www.python.org/) and the following built-in python3  packages:

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

#### MariaDB User Permissions

For the backup user, the following permissions are recommended:

```sql
GRANT SELECT, LOCK TABLES, SHOW VIEW, EVENT, TRIGGER, RELOAD, PROCESS, REPLICATION CLIENT ON <db_name>.* TO '<user>'@'<server>';
```

These permissions ensure the backup user can access all required data and metadata while maintaining a principle of least privilege.

## PostgreSQL Specific Configuration

The PostgreSQL backup script requires you to configure connection settings using script variables and a `.pgpass` file for authentication.

| Variable         | Variable Type | Description                                              | Is Required          |
|------------------|---------------|----------------------------------------------------------|----------------------|
| `BACKUP_GLOBALS` | `bool`        | Enables/Disables PostgreSQL Globals backup               | Yes (default `True`) |
| `PG_HOST`        | `str`         | Sets the PostgreSQL server IP                            | Yes                  |
| `PG_USER`        | `str`         | Sets the PostgreSQL user used to connect to the database | Yes                  |

#### `.pgpass` Creation Guide

```shell
touch $HOME/.pgpass;

echo "<pg_ip_address>:<pg_port_address>:*:<pg_username>:<pg_user_password>" > $HOME/.pgpass;

chmod 600 $HOME/.pgpass;
```

#### PostgreSQL User Permissions

For regular database backups, create a dedicated backup user with limited permissions:

```sql
CREATE USER backup_user WITH PASSWORD 'secure_password';

-- Grant necessary privileges
GRANT CONNECT ON DATABASE your_database TO backup_user;
GRANT USAGE ON SCHEMA public TO backup_user;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO backup_user;
GRANT SELECT ON ALL SEQUENCES IN SCHEMA public TO backup_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO backup_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON SEQUENCES TO backup_user;
```

For backing up PostgreSQL globals (roles, tablespaces, etc.) and all databases, you'll need broader permissions:

```sql
CREATE USER backup_admin WITH PASSWORD 'very_secure_password';

-- Grant role to connect to all databases
GRANT CONNECT ON DATABASE postgres TO backup_admin;
ALTER USER backup_admin WITH SUPERUSER;

-- Restrict connections to specific hosts/networks
CREATE RULE backup_admin_connection AS ON CONNECTION TO postgres
WHERE pg_catalog.inet_client_addr() != '<connection_ip>'
DO INSTEAD NOTHING;
```

Alternatively, consider using an existing database superuser account with appropriate connection restrictions in pg_hba.conf:

```
# pg_hba.conf entry restricting superuser to backup server only
host    all     backup_admin     192.168.1.100/32    scram-sha-256
```

## Usage

To run this script you need to issue the following commands:

```properties
./path/to/database_type/main.py
# or
python3 /path/to/database_type/main.py
```
