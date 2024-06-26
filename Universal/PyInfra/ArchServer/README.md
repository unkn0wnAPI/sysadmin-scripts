# ArchLinux Server Deployment (PyInfra)

This is a script written with PyInfra, that automates the task of configuring and setting up freshly installed Arch Linux Server.

## Getting Started

The scripts requires specific packages and/or software (See [Prerequisites](#prerequisites) for more information).

### Prerequisites

This tool uses [Python 3](https://www.python.org) and the following python packages:

* pyinfra (v2)

To easily install them on a system that allows installing packages using [pip](https://pypi.org/project/pip), you can use the following command:

```properties
pip install -r requirements.txt
```

In case you encounter the following output: `error: externally-managed-environment`, it means that your OS does not allow installation of python packages using pip.

If that's the case you can eliminate this problem by either:

* Crating an instance of python virtual environment `venv` and use the script from there,
* Install the required packages using your OS package manager.

## Configuration

This script parameters (i.e. target hosts and their settings) can be change by modifying `inventory` (defines list of host accessed by pyInfra) or/and `server_config` (defines script options that can be different depending on the desired outcome) blocks in `inventory.py`.

This file is structured as described in the pyInfra documentation, which can be found [here](https://docs.pyinfra.com/en/2.x/index.html). Your changes must be structured and available with the pyInfra schema.

For other PyInfra runtime configuration that can be accessed from the CLI:

```properties
pyinfra --help
```

Sample configuration is provided in the repository under the name: `inventory.py.sample`.

### `inventory` block configuration

| Variable Name             | Description                                                               |
| ------------------------- | ------------------------------------------------------------------------- |
| `ssh_hostname`            | Sets the host ip address or hostname                                      |
| `ssh_port`                | Sets the ssh port used when connecting to target host                     |
| `ssh_user`                | Sets the ssh user used during configuration                               |
| `ssh_password`            | Sets the ssh user's password used during configuration                    |

More configurations options and/or different ways of connecting with the target hosts can be found [here](https://docs.pyinfra.com/en/2.x/connectors.html).

### `server_config` block configuration

| Variable Name             | Description                                                               |
| ------------------------- | ------------------------------------------------------------------------- |
| `MIRROR_REGION`           | Sets the desired pacman mirror region                                     |
| `ZEROTIER_NETWORK_ID`     | Sets the Zerotier network id used when configuring zerotier service       |
| `SWAPFILE_SIZE`           | Sets the size of the system swap file (Default: 4G)                       |
| `LC_TIME_LOCALE`          | Sets the value of the LC_TIME locale variable (Default: en_US.UTF-8)      |

## Usage

To run this script you need to issue the following commands:

```properties
pyinfra inventory.py deploy.py <additional_pyinfra_options>
```

## Contributors

List of all users which contributed to this script:

* [Jakub Majcherski](https://github.com/majcher01)
