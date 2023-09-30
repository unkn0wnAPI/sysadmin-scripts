# Miktorik Configuration Generator

A handy script for quick and easy deployment of Mikrotik RouterOS Devices.  

## Getting Started

The scripts requires specific software and/or packages (See [Prerequisites](#prerequisites) for more information).

### Prerequisites

Tools and elements required to successfully use the script:

* [Python 3](https://www.python.org/) installed on the machine used for generation.
* Mikrotik RouterOS network appliance
  * Remote access to said device;
  * Password protected user;
  * SSH configured and enabled for said user.

## Configuration

The scripts ships with default configuration to the following Mikrotik device aspects:

* Interfaces Configuration:
  * LAN Interface;
  * WAN Interface;
  * Management Interface;
* Network Configuration:
  * WAN Network Configuration (Static/Dynamic);
  * LAN Network Configuration
  * Firewall Configuration (Interface Separation/Basic/Advanced)
  * UPnP
* RouterOS Configuration:
  * SSH Port
  * Services

Disclaimer: **The default configuration is based on guidelines and requirements for my study project. It is highly advised to modify the configuration based on your needs!**

## Usage

To run this script you need to issue the following commands:

```properties
# On windows
python main.py

# On Linux/Unix based systems
python3 main.py
```

After successfully executing the script, a `configuration.rsc` file will be created. To execute it on the Mikrotik device you need to send it to the device (for example, by the use of SSH):

```properties
# Send file to Mikrotik Device using SCP (SSH)
scp -P <ROUTEROS_SSH_PORT> configuration.rsc <ROUTEROS_USER>@<ROUTEROS_HOST>:.

# Execute the script remotely using SSH
ssh $ROUTEROS_USER@$ROUTEROS_HOST -p $ROUTEROS_SSH_PORT "/import file-name=configuration.rsc"
```
