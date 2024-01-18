#!/usr/bin/python3

#
## Script Name: Portainer API Utils
## Author:      unkn0wnAPI [https://github.com/unkn0wnAPI]
## Information: Custom script for interfacing with Portainer Instance
#

#
## Imports
#
import requests, argparse, json, urllib3
from colorama import Fore as F, Style as S
from dotenv import dotenv_values, find_dotenv
from datetime import datetime

#
## Init configuration variable
#
CONFIGS = {}
REQ_HEADERS = {}

#
## Core Functions
#
def app_notification(mode: str):
    if mode == 'in':
        print('####################################')
        print(('Portainer Agent - Version: 1.0').center(36))
        print(('Written by: unkn0wnAPI').center(36))
        print((f'Time: {datetime.now().strftime("%d/%m/%Y - %H:%M:%S")}').center(36))
        print('####################################\n')
    elif mode == 'out':
        print(F'\n{F.LIGHTMAGENTA_EX}Part of sysadmin-scripts Github Repository [https://github.com/unkn0wnAPI/sysadmin-scripts]{S.RESET_ALL}\n')

def pprint(severity: str, message: str):
    if severity == "INF":
        print(f"{F.LIGHTBLUE_EX}[INF] {message}{S.RESET_ALL}")
    elif severity == "ERR":
        print(f"{F.LIGHTRED_EX}[ERR] {message}{S.RESET_ALL}")
    elif severity == "ACT":
        print(f"{F.LIGHTGREEN_EX}[ACT] {message}{S.RESET_ALL}")
    elif severity == "WRN":
        print(f"{F.YELLOW}[WRN] {message}{S.RESET_ALL}")
    else:
        print(f"{message}")

def init_arg_parse():
    args = argparse.ArgumentParser(description=f'Custom script to manage Portainer instance', epilog="Written by unkn0wnAPI, part of sysadmin-scripts [https://github.com/unkn0wnapi/sysadmin-scripts]")
    args.add_argument('--no-env', '-ne', action='store_true', dest='noenv', help='Don\'t load variables from .env file')
    args.add_argument('--endpoint', '-e', action='store', dest="endpoint", default='', help='Portainer instance endpoint (either IP or URL, which is accessible)')
    args.add_argument('--api-key', '-k', action='store', dest='key', default='', help='Portainer API key used to authenticate scripts actions')
    args.add_argument('--unsafe-tls', '-t', action='store_true', dest='unsafe_tls', help='Don\'t verify portainer TLS certificate')
    args.add_argument('--skip-check', '-sc', action='store_true', dest='skip_check', help='Skip initial connectivity check to the portainer endpoint')
    
    return args.parse_args()

def load_configs():
    global CONFIGS, REQ_HEADERS

    ARGS = init_arg_parse()
    if ARGS.noenv == False:
        if find_dotenv() is None or find_dotenv() == "":
            pprint("ERR", f"Unable to load .env file in working directory, exiting")
            exit(1)
        else:
            CONFIGS = dotenv_values(".env")

            # Change str to boolean, using in-built methods results in "False" being converted to True (boolean)
            if CONFIGS.get("VERIFY_TLS_CERT") == "False":
                CONFIGS.update({"VERIFY_TLS_CERT": False})
                urllib3.disable_warnings()
            else:
                CONFIGS.update({"VERIFY_TLS_CERT": True})
            
            if CONFIGS.get("SKIP_CONNECTIVITY_CHECK") == "False":
                CONFIGS.update({"SKIP_CONNECTIVITY_CHECK": False})
            else:
                CONFIGS.update({"SKIP_CONNECTIVITY_CHECK": True})
            
            pprint("ACT", f"Loaded script configuration from .env file")
    else:
        pprint("INF", "Variables from .env file won't be loaded, reading script arguments")
        CONFIGS = { "PORTAINER_API_ENDPOINT": ARGS.endpoint, "PORTAINER_API_KEY": ARGS.key, "VERIFY_TLS_CERT": ARGS.unsafe_tls, "SKIP_CONNECTIVITY_CHECK": ARGS.skip_check }

        if (CONFIGS.get("PORTAINER_API_ENDPOINT") == "" or CONFIGS.get("PORTAINER_API_KEY") == "" or CONFIGS.get("VERIFY_TLS_CERT") == ""):
            pprint("ERR", "Missing required variables, exiting")
            exit(1)
        else:
            pprint("ACT", "Loaded script configuration from arguments")
    
    REQ_HEADERS = { "X-API-Key": CONFIGS.get('PORTAINER_API_KEY'), 'Content-Type': 'application/json' }

def check_portainer_availability() -> list:
    global REQ_HEADERS, CONFIGS

    if CONFIGS.get('SKIP_CONNECTIVITY_CHECK') == False:
        try:
            pprint("INF", "Checking connectivity and access to portainer endpoint...")
            check = requests.get(f"{CONFIGS.get('PORTAINER_API_ENDPOINT')}/motd", headers=REQ_HEADERS, verify=bool(CONFIGS.get("VERIFY_TLS_CERT")))
                
            if check.status_code == 200:
                pprint("ACT", "Connection and authorization was successful")
            else:
                pprint("ERR", "Unable to authenticate, exiting")
                exit(1)

        except Exception:
            pprint("ERR", "Encountered an error whilst connecting to the endpoint, exiting")
            exit(1)
    else:
        pprint('WRN', "Skipping initial connectivity check")
        check = None

def get_instance_data() -> list:
    global REQ_HEADERS
    data = []
    stacksList = []

    stacksReq = requests.get(f"{CONFIGS.get('PORTAINER_API_ENDPOINT')}/stacks", headers=REQ_HEADERS, verify=bool(CONFIGS.get("VERIFY_TLS_CERT")))
    stacks = stacksReq.json()

    for stack in stacks:
        stacksList.append({ "StackName": stack.get('Name'), "StackId": stack.get('Id') })

    endpointReq = requests.get(f"{CONFIGS.get('PORTAINER_API_ENDPOINT')}/endpoints/{stacks[0].get('EndpointId')}", headers=REQ_HEADERS, verify=bool(CONFIGS.get("VERIFY_TLS_CERT")))
    endpointData = endpointReq.json()

    data.append({ "EndpointId": stacks[0].get('EndpointId'), "EndpointName": endpointData.get('Name') })
    data.append(stacksList)

    stacksReq = None
    endpointReq = None
    return data

#
## Functions
#
def update_stack_containers(stacks: list) -> list:
    update_logs = []

    for stack in stacks[1]:
        stopStackReq = requests.post(f"{CONFIGS.get('PORTAINER_API_ENDPOINT')}/stacks/{stack.get('StackId')}/stop?endpointId={stacks[0].get('EndpointId')}", headers=REQ_HEADERS, verify=bool(CONFIGS.get("VERIFY_TLS_CERT")))

        getStackComposeReq = requests.get(f"{CONFIGS.get('PORTAINER_API_ENDPOINT')}/stacks/{stack.get('StackId')}/file?endpointId={stacks[0].get('EndpointId')}", headers=REQ_HEADERS, verify=CONFIGS.get("VERIFY_TLS_CERT"))
        stackCompose = getStackComposeReq.json()

        getStackEnvReq = requests.get(f"{CONFIGS.get('PORTAINER_API_ENDPOINT')}/stacks/{stack.get('StackId')}", headers=REQ_HEADERS, verify=bool(CONFIGS.get("VERIFY_TLS_CERT")))
        stackEnv = getStackEnvReq.json()
        
        data = {
            "id": stack.get('StackId'),
            "StackFileContent": stackCompose.get('StackFileContent'),
            "Env": stackEnv.get('Env'),
            "Prune": False,
            "PullImage": True
        }
        redeployStackReq = requests.put(f"{CONFIGS.get('PORTAINER_API_ENDPOINT')}/stacks/{stack.get('StackId')}?endpointId={stacks[0].get('EndpointId')}", headers=REQ_HEADERS, data=json.dumps(data), verify=bool(CONFIGS.get("VERIFY_TLS_CERT")))
        update_logs.append({ "StackId": stack.get('StackId'), "RedeployStatus": redeployStackReq.status_code })
        
        stopStackReq = None
        getStackComposeReq = None
        getStackEnvReq = None
        redeployStackReq = None

    return update_logs

# TODO: Implement ability to run custom script on actions
def run_custom_script():
    pass

#
## Script Start point
#
def main():
    global CONFIGS
    
    app_notification('in')

    load_configs()
    check_portainer_availability()
    
    pprint('INF', 'Obtaining portainer instance information')
    infrastructure = get_instance_data()
    pprint('ACT', f'Found {len(infrastructure[0]) / 2} endpoints [No. of stacks: {len(infrastructure[1])}]')

    pprint('INF', f'Updating stacks on endpoint no. {infrastructure[0].get("EndpointId")} [{infrastructure[0].get("EndpointName")}]')
    statuses = update_stack_containers(stacks=infrastructure)
    for status in statuses:
        if status.get('RedeployStatus') == 200:
            pprint('ACT', f"Stack no. {status.get('StackId')} updated successfully")
        else:
            pprint('ERR', f"Stack no. {status.get('StackId')} failed to update")
    
    app_notification('out')


if __name__ == "__main__":
    main()