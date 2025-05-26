# Directory Backup Script

This script is a utility for backing up directories in a Linux environment. It allows you to create backups of specified directories, with options for compression, exclusion, scheduling, and retention policies.

## Features
- Automated directory backups
- Compression options
- Configurable backup schedules
- Configurable list of excluded directories
- Customizable retention policies
- Detailed logging

## Getting Started

The scripts requires specific packages (See [Prerequisites](#prerequisites) for more information).

### Prerequisites

This tool uses [GNU TAR](https://www.gnu.org/software/tar/) for compression, [Python 3](https://www.python.org/) and the following built-in python3 packages:

* subprocess
* requests
* os
* logging
* socket
* gzip
* datetime
* Path

## Configuration

Each database backup script can be configured using the following variables:

| Variable          | Variable Type | Description                                                                              | Is Required            |
|-------------------|---------------|------------------------------------------------------------------------------------------|------------------------|
| `BACKUP_DIR`      | `Path`        | Sets the root directory for backups and logs                                             | Yes                    |
| `LOG_DIR`         | `Path`        | Sets the logs directory name (automatically populated if not specified)                  | No (Auto Populated)    |
| `LOG_FILE_PREFIX` | `str`         | Sets the prefix for the log files                                                        | Yes                    |
| `SLACK_WEBHOOK`   | `str`         | Slack WebHook URL for error notifications                                                | No (Works w/o it)      |
| `MAX_BACKUPS`     | `int`         | Maximum number of backup files to retain                                                 | Yes                    |
| `INCLUDE_PATHS`   | `list[str]`   | List of directories to backup (Absolute paths must be used)                              | Yes                    |
| `EXCLUDE_PATHS`   | `list[str]`   | List of directories to exclude from backup (Absolute paths must be used)                 | No                     |

## Usage

To run this script you need to issue the following commands:

```properties
./path/to/main.py
# or
python3 /path/to/main.py
```
