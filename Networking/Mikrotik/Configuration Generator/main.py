#
## Script Name: Mikrotik Configuration Generator
## Author:      unkn0wnAPI [https://github.com/unkn0wnAPI]
## Information: Semi-configurable Mikrotik Configuration Generator
#

#
## Imports
#
from itertools import permutations

#
## Configuration
#
OUTPUT_FILE = "configuration.rsc"

## Interface Configuration
INTERFACE_CONFS = {
    #    INTERFACE                LIST NAME               INTERFACE COMMENT              Network Settings [Address/CIDR]
    1: { "interface": "ether1", "int_list_name": "WAN", "int_comment": "WAN Interface", "network": None },
    2: { "interface": "ether2", "int_list_name": "MGMT", "int_comment": "MGMT Interface", "network": "10.0.0.1/16" },
    3: { "interface": "ether3", "int_list_name": "LAN", "int_comment": "LAN1 Interface", "network": "10.1.0.1/16" },
    4: { "interface": "ether4", "int_list_name": "LAN", "int_comment": "LAN2 Interface", "network": "10.2.0.1/16" },
}

## IP Configuration
# WAN Interface
WAN_USE_NAT = True
WAN_USE_DHCP = True
WAN_STATIC_CONFS = {
    "address": '192.168.69.128/24', 
    "gateway": '192.168.69.2', 
    "dns-servers": ['1.1.1.1', '1.0.0.1']
}

# UPnP
UPNP_ENABLED = True
UPNP_CONFS = {
    "EXTERNAL_INT": 'ether1',
    "INTERNAL_INT": 'ether3'
}

## Firewall
FIREWALL_INT_SEPARATION = True
FIREWALL_ADVANCED_PROTECTION = False

## DHCP Server
DHCP_LAN_CONFIGS = {
    # ID Pool Name                 IP Range                              INT                    Network Params [Network, DNS Server, Gateway, Domain (Used for static DNS entries)]
    1: { "pool_name": 'dhcp_lan1', "ip_range": '10.1.0.10-10.1.255.254', "interface": 'ether3', "network_params": ["10.1.0.0/16", "10.1.0.1", "10.1.0.1", ""] },
    2: { "pool_name": 'dhcp_lan2', "ip_range": '10.2.0.10-10.2.255.254', "interface": 'ether4', "network_params": ["10.2.0.0/16", "10.2.0.1", "10.2.0.1", ""] },
} # TODO: Automatic DHCP Configuration generator

CREATE_STATIC_DNS_ENTRIES = False
DHCP_STATIC_DNS_ENTRIES = {
    #    DNS Address    TTL          Entry Comment  Entry Type  Entry Specific Data
    1: { "address": '', "ttl": '1d', 'comment': '', "type": '', "data": []}
}
# WARNING! Each DNS entry type has its own entry elements, you need to specify them manually in CORRECT ORDER in the data array
# DNS Entry Data Order:
#  - A/AAAA: "data": ["Device IP Address"]
#  - CNAME: "data": ["Service CNAME"]
#  - FWD: "data": ["Forward IP Address"]
#  - MX: "data": ["MX Preference", "MX Exchange IP Address/Domain"]
#  - NS: "data": ["NS IP Address/Domain"]
#  - NXDOMAIN: "data": []
#  - SRV: "data": ["SRV Priority", "Srv Weight", "SRV Port", "SRV Target]
#  - TXT: "data": ["Text"]

## Security
# Services
ROS_DISABLED_SERVICES = ['telnet', 'ftp', 'www-ssl', 'api', 'www']
ROS_LIMIT_WINBOX_TO_MGMT_INT = False
ROS_ENABLE_BANDWITH_SERVER = False
ROS_ENABLE_PROXY = False
ROS_ENABLE_SOCKS = False
ROS_ENABLE_DDNS = False
ROS_HIDE_PIN = True 
ROS_SSH_PORT = 22

#
## Functions
#
def gen_interface() -> list:
    output = []
    lan_list_created = False

    for conf in INTERFACE_CONFS.values():
        if not lan_list_created:
            output.append(f'/interface list add name={conf["int_list_name"]}')
        if conf["int_list_name"] == "LAN":
             lan_list_created = True
        output.append(f'/interface list member add list={conf["int_list_name"]} interface={conf["interface"]}')
        output.append(f'/interface comment {conf["interface"]} comment="{conf["int_comment"]}"')
        if conf["network"] != None:
            output.append(f'/ip address add address={conf["network"]} network={str(conf["network"])[:-4]}0 interface={conf["interface"]}')

    return output

def gen_network() -> list:
    output = []

    if WAN_USE_NAT:
        output.append(f'/ip firewall nat add chain=srcnat out-interface=ether1 action=masquerade')
    
    if not WAN_USE_DHCP:
        output.append(f'/ip address add address={WAN_STATIC_CONFS["address"]} interface=ether1')
        output.append(f'/ip route add gateway={WAN_STATIC_CONFS["gateway"]}')
        output.append(f'/ip dns set servers={",".join(WAN_STATIC_CONFS["dns-servers"])}')
    
    if UPNP_ENABLED:
        output.append(f'/ip upnp set enabled=yes')
        output.append(f'/ip upnp interfaces add interface={UPNP_CONFS["EXTERNAL_INT"]} type=external')
        output.append(f'/ip upnp interfaces add interface={UPNP_CONFS["INTERNAL_INT"]} type=internal')
        output.append(f'/ip upnp interfaces enable 0,1')
    
    return output

def gen_firewall() -> list:
    output = []
    int_list = []

    for conf in INTERFACE_CONFS.values():
        if conf["network"] != None:
            int_list.append(conf["network"])
    
    if FIREWALL_INT_SEPARATION and len(int_list) > 1:
        for pair in permutations(int_list, 2):
            output.append(f'/ip firewall filter add chain=forward src-address={pair[0]} dst-address={pair[1]} action=drop comment="Block {pair[0]}<->{pair[1]}"')

    # Basic firewall rules [based on Miktotik Configuration Documentation]
    output.append('/ip firewall filter add chain=forward action=fasttrack-connection connection-state=established,related comment="Fast-track for established,related";')
    output.append('/ip firewall filter add chain=forward action=accept connection-state=established,related comment="Accept established,related";')
    output.append('/ip firewall filter add chain=forward action=drop connection-state=new connection-nat-state=!dstnat in-interface=ether1 comment="Drop access to clients behind NAT from WAN"')
    
    if FIREWALL_ADVANCED_PROTECTION:
        address_list_entries = [
        #   Address      Comment
            ["0.0.0.0/8", "RFC6890"],
            ["172.16.0.0/12", "RFC6890"],
            ["192.168.0.0/16", "RFC6890"],
            ["10.0.0.0/8", "RFC6890"],
            ["169.254.0.0/16", "RFC6890"],
            ["127.0.0.0/8", "RFC6890"],
            ["224.0.0.0/4", "Multicast"],
            ["198.18.0.0/15", "RFC6890"],
            ["192.0.0.0/24", "RFC6890"],
            ["192.0.2.0/24", "RFC6890"],
            ["198.51.100.0/24", "RFC6890"],
            ["203.0.113.0/24", "RFC6890"],
            ["100.64.0.0/10", "RFC6890"],
            ["240.0.0.0/4", "RFC6890"],
            ["192.88.99.0/24", "RFC3068"]
        ]

        for entry in address_list_entries:
            output.append(f'/ip firewall address-list add address={entry[0]}, comment={entry[1]}, list=not_in_internet')

        output.append(f'/ip firewall filter add action=drop chain=forward comment="Drop invalid" connection-state=invalid log=yes log-prefix=invalid')
        output.append(f'/ip firewall filter add action=drop chain=forward comment="Drop tries to reach not public addresses from LAN" dst-address-list=not_in_internet in-interface=LAN log=yes log-prefix=!public_from_LAN out-interface=!LAN')
        output.append(f'/ip firewall filter add action=drop chain=forward comment="Drop incoming packets that are not NATted" connection-nat-state=!dstnat connection-state=new in-interface=ether1 log=yes log-prefix=!NAT')
        output.append(f'/ip firewall filter add action=jump chain=forward protocol=icmp jump-target=icmp comment="jump to ICMP filters"')
        output.append(f'/ip firewall filter add action=drop chain=forward comment="Drop incoming from internet which is not public IP" in-interface=ether1 log=yes log-prefix=!public src-address-list=not_in_internet')

    return output

def gen_dhcp() -> list:
    output = []

    for conf in DHCP_LAN_CONFIGS.values():
        output.append(f'/ip pool add name={conf["pool_name"]} ranges={conf["ip_range"]}')
        output.append(f'/ip dhcp-server add address-pool={conf["pool_name"]} interface={conf["interface"]} name={conf["pool_name"]}')
        output.append(f'/ip dhcp-server network add address={conf["network_params"][0]} dns-server={conf["network_params"][1]} gateway={conf["network_params"][2]} domain={conf["network_params"][3]}')

    return output

def gen_ossec() -> list:
    output = []

    # Winbox connectivity
    if ROS_LIMIT_WINBOX_TO_MGMT_INT:
        output.append(f'/tool mac-server set allowed-interface-list={INTERFACE_CONFS[2]["int_list_name"]}')
        output.append(f'/tool mac-server mac-winbox set allowed-interface-list={INTERFACE_CONFS[2]["int_list_name"]}')
        output.append(f'/ip neighbor discovery-settings set discover-interface-list={INTERFACE_CONFS[2]["int_list_name"]}')

    # ROS Services
    output.append(f'/ip service disable {",".join(ROS_DISABLED_SERVICES)}')

    if not ROS_ENABLE_BANDWITH_SERVER: 
        output.append(f'/tool bandwidth-server set enabled=no')
    if not ROS_ENABLE_PROXY: 
        output.append(f'/ip proxy set enabled=no')
    if not ROS_ENABLE_SOCKS: 
        output.append(f'/ip socks set enabled=no')
    if not ROS_ENABLE_DDNS: 
        output.append(f'/ip cloud set ddns-enabled=no update-time=no')

    output.append(f'/ip service set ssh port={ROS_SSH_PORT}')

    return output

def gen_dns() -> list:
    output = []

    # Allow for static DNS entries defined in RouterOS & DNS Caching
    output.append(f'/ip dns set allow-remote-requests=yes')

    # Static DNS Entries
    if CREATE_STATIC_DNS_ENTRIES:
        for entry in DHCP_STATIC_DNS_ENTRIES.values():
            # Python Version < 3.10 Friendly type checking
            if entry["type"] == "A" or entry["type"] == "AAAA":
                output.append(f'/ip dns static add name={entry["address"]} type={entry["type"]} ttl={entry["ttl"]} address={entry["data"][0]} comment="{entry["comment"]}"')
            elif entry["type"] == "CNAME":
                output.append(f'/ip dns static add name={entry["address"]} type={entry["type"]} ttl={entry["ttl"]} cname={entry["data"][0]} comment="{entry["comment"]}"')
            elif entry["type"] == "FWD":
                output.append(f'/ip dns static add name={entry["address"]} type={entry["type"]} ttl={entry["ttl"]} forward-to={entry["data"][0]} comment="{entry["comment"]}"')
            elif entry["type"] == "MX":
                output.append(f'/ip dns static add name={entry["address"]} type={entry["type"]} ttl={entry["ttl"]} mx-preference={entry["data"][0]} mx-exchange={entry["data"][1]} comment="{entry["comment"]}"')
            elif entry["type"] == "NS":
                output.append(f'/ip dns static add name={entry["address"]} type={entry["type"]} ttl={entry["ttl"]} ns={entry["data"][0]} comment="{entry["comment"]}"')
            elif entry["type"] == "NXDOMAIN":
                output.append(f'/ip dns static add name={entry["address"]} type={entry["type"]} ttl={entry["ttl"]} comment="{entry["comment"]}"')
            elif entry["type"] == "SRV":
                output.append(f'/ip dns static add name={entry["address"]} type={entry["type"]} ttl={entry["ttl"]} srv-priority={entry["data"][0]} srv-weight={entry["data"][1]} srv-port={entry["data"][2]} srv-target={entry["data"][3]} comment="{entry["comment"]}"')
            elif entry["type"] == "TXT":
                output.append(f'/ip dns static add name={entry["address"]} type={entry["type"]} ttl={entry["ttl"]} text={entry["data"][0]} comment="{entry["comment"]}"')
            else:
                print(f"Unable to create DNS entry! [Unknown entry type: {entry['type']}]")

    # Block access to local DNS server from WAN Interface
    output.append(f'/ip firewall filter add chain=input action=drop protocol=tcp in-interface=ether1 dst-port=53')
    output.append(f'/ip firewall filter add chain=input action=drop protocol=udp in-interface=ether1 dst-port=53')

    # Allow access to local DNS server from LAN interfaces
    for conf in INTERFACE_CONFS.values():
        if conf["network"] != None:
            output.append(f'/ip firewall filter add chain=input action=accept protocol=tcp in-interface={conf["interface"]} dst-port=53')
            output.append(f'/ip firewall filter add chain=input action=accept protocol=udp in-interface={conf["interface"]} dst-port=53')

    return output
#
## Script Start point
#
def main():
    print("[INFO] Mikrotik configuration generator started")
    interface_confs = gen_interface()
    network_confs = gen_network()
    dhcp_confs = gen_dhcp()
    firewall_confs = gen_firewall()
    ossec_confs = gen_ossec()

    print(f"[INFO] Saving configuration script to file {OUTPUT_FILE}")
    with open(OUTPUT_FILE, 'w') as config_file:
        config_file.write(f':put [/log info "Importing Interface Configuration"]; \n')
        for conf in interface_confs:
            config_file.write(f":put [{conf}]; \n")

        config_file.write(f':put [/log info "Importing Network Configuration"]; \n')
        for conf in network_confs:
            config_file.write(f":put [{conf}]; \n")
        
        config_file.write(f':put [/log info "Importing DHCP Server Configuration"]; \n')
        for conf in dhcp_confs:
            config_file.write(f":put [{conf}]; \n")

        if CREATE_STATIC_DNS_ENTRIES:
            config_file.write(f':put [/log info "Importing DHCP Server Configuration"]; \n')
            for conf in dhcp_confs:
                config_file.write(f":put [{conf}]; \n")

        config_file.write(f':put [/log info "Importing Firewall Configuration"]; \n')
        for conf in firewall_confs:
            config_file.write(f":put [{conf}]; \n")

        config_file.write(f':put [/log info "Importing RouterOS Configuration"]; \n')
        for conf in ossec_confs:
            config_file.write(f":put [{conf}]; \n")

if __name__ == "__main__":
    main()