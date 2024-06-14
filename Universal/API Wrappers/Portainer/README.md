# Portainer Updater

This is a script that automates the task of updating docker stacks created and managed by the Portainer container management system.

## Getting Started

The scripts requires specific packages (See [Prerequisites](#prerequisites) for more information).

### Prerequisites

This tool uses [Python 3](https://www.python.org/) and the following python packages:

* requests
* python-dotenv
* colorama

To easily install them on a system that allows installing packages using [pip](https://pypi.org/project/pip/), you can use the following command:

```properties
pip install -r requirements.txt
```

In case you encounter the following output: `error: externally-managed-environment`, it means that your OS does not allow installation of python packages using pip.

If that's the case you can eliminate this problem by either:

* Crating an instance of python virtual environment `venv` and use the script from there,
* Install the required packages using your OS package manager.

## Configuration

This tool can be configured either using a `.env` file or by passing arguments in the cli.

### Environment File (`.env`) Method

| Variable Name             | Description                                                               | Required (Default) |
| ------------------------- | ------------------------------------------------------------------------- | ------------------ |
| `PORTAINER_API_ENDPOINT`  | Sets the portainer endpoint base address                                  | Yes (None)         |
| `PORTAINER_API_KEY`       | Sets the API key used to authenticate with the Portainer Endpoint         | Yes (None)         |
| `VERIFY_TLS_CERT`         | Enables/Disables TLS Certificate checks                                   | Yes ("True")       |
| `SKIP_CONNECTIVITY_CHECK` | Enables/Disables initial endpoint connectivity check                      | Yes ("False")      |
| `SKIP_ENDPOINTS_LIST`     | Specifies endpoints that should be skipped by the script (Delimiter: `,`) | Yes ("")           |

Remember: **Do not use `--no-env/-ne` if you want to use the configuration from `.env`**

### Arguments Method

| Script argument           | Description                                                               | Required                         |
| ------------------------- | ------------------------------------------------------------------------- | -------------------------------- |
| `--no-env/-ne`            | Disables the use of `.env` file                                           | No                               |
| `--endpoint/-e`           | Sets the portainer endpoint base address                                  | Yes (when not using `.env` file) |
| `--api-key/-k`            | Sets the API key used to authenticate with the Portainer Endpoint         | Yes (when not using `.env` file) |
| `--skip-endpoints/-se`    | Specifies endpoints that should be skipped by the script (Delimiter: `,`) | Yes (when not using `.env` file) |
| `--unsafe-tls/-t`         | Skip TLS Certificate checks                                               | Yes (when not using `.env` file) |
| `--skip-check/-sc`        | Skip initial endpoint connectivity check                                  | Yes (when not using `.env` file) |

Detailed information can be found by running script with `--help/-h` flag.

## Usage

To run this script you need to issue the following commands:

```properties
./main.py --no-env <options> # When `.env` file is not used
./main.py # When `.env` file is used
# or
python3 main.py --no-env <options> <input_directory> # When `.env` file is not used
python3 main.py # When `.env` file is used
```
