# Cisco Password (Type 7) Recovery  Tool

A quirky script for recovering passwords encrypted using `service password-encryption` (Type 7) from old Cisco networking gear. 
Made to automate the recovery and exploration of old equipment found in lab storage.

> [!WARNING]
> ## Disclaimer
> This tool is provided for **educational and research purposes only**. It is intended exclusively for recovering passwords from your own equipment or systems you have explicit permission to access.
> 
> **The author accepts no responsibility or liability** for any misuse of this script or for any unauthorized access attempts. Use of this tool against systems without proper authorization may violate computer crime laws and other regulations.
> 
> By using this script, you acknowledge that you are solely responsible for how it is used and agree to use it only in legal and ethical ways.

## Getting Started

The scripts may require specific software and/or packages (See [Prerequisites](#prerequisites) for more information).

### Prerequisites

Tools and elements required to successfully use the script:

* [Python 3](https://www.python.org/) installed on the machine used for generation.

## Configuration

This script requires you to provide an array of passwords you wish to recover (saved in a variable as a list).

## Usage

To run this script you need to issue the following commands:

```properties
# On windows
python main.py

# On Linux/Unix based systems
python3 main.py
# or
chmod +x ./main.py;
./main.py
```
