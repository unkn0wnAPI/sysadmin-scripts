#!/usr/bin/python3

#
## Script Name: Portainer Updater
## Author:      unkn0wnAPI [https://github.com/unkn0wnAPI]
## Information: Automated script that updates your Portainer stacks for you
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
    args = argparse.ArgumentParser(description=f'Automated script that updates your Portainer stacks for you', epilog="Written by unkn0wnAPI, part of sysadmin-scripts [https://github.com/unkn0wnapi/sysadmin-scripts]")
    args.add_argument('--no-env', '-ne', action='store_true', dest='noenv', help='Don\'t load variables from .env file')
    args.add_argument('--endpoint', '-e', action='store', dest="endpoint", default='', help='Portainer instance endpoint (IP or URL)')
    args.add_argument('--api-key', '-k', action='store', dest='key', default='', help='Portainer API key used to authenticate scripts actions')
    args.add_argument('--skip-endpoints', '-se', action='store', default='', dest='skip_endpoints', help='List of endpoint names that will be excluded during updates (Delimiter: ",")')
    args.add_argument('--unsafe-tls', '-t', action='store_false', dest='unsafe_tls', help='Don\'t verify portainer TLS certificate')
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
        
        CONFIGS = { "PORTAINER_API_ENDPOINT": ARGS.endpoint, "PORTAINER_API_KEY": ARGS.key, "VERIFY_TLS_CERT": ARGS.unsafe_tls, "SKIP_CONNECTIVITY_CHECK": ARGS.skip_check, "SKIP_ENDPOINTS_LIST": ARGS.skip_endpoints }

        if (CONFIGS.get("PORTAINER_API_ENDPOINT") == "" or CONFIGS.get("PORTAINER_API_KEY") == "" or CONFIGS.get("VERIFY_TLS_CERT") == ""):
            pprint("ERR", "Missing required variables, exiting")
            exit(1)
        else:
            if ARGS.unsafe_tls == False:
                urllib3.disable_warnings()
            pprint("ACT", "Loaded script configuration from arguments")
    
    REQ_HEADERS = { "X-API-Key": CONFIGS.get('PORTAINER_API_KEY'), 'Content-Type': 'application/json' }

def check_portainer_availability():
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

def get_instance_data() -> list:
    global REQ_HEADERS
    data = []
    endpoints = []
    stacksList = []

    endpointReq = requests.get(f"{CONFIGS.get('PORTAINER_API_ENDPOINT')}/endpoints", headers=REQ_HEADERS, verify=bool(CONFIGS.get("VERIFY_TLS_CERT")))
    for endpoint in endpointReq.json():
        endpoints.append({ "EndpointId": endpoint.get('Id'), "EndpointName": endpoint.get('Name') }) 

    for endpoint in endpoints:
        json_filter = {
            'EndpointId': endpoint.get('EndpointId')
        }

        stacksReq = requests.get(f"{CONFIGS.get('PORTAINER_API_ENDPOINT')}/stacks?filters={json.dumps(json_filter)}", headers=REQ_HEADERS, verify=bool(CONFIGS.get("VERIFY_TLS_CERT")))
        stacks = stacksReq.json()

        for stack in stacks:
            stacksList.append({ "StackName": stack.get('Name'), "StackId": stack.get('Id'), "EndpointId": json_filter.get('EndpointId') })

    data.append(endpoints)
    data.append(stacksList)
    return data

#
## Functions
#
def update_stack_containers(stacks: list, endpointId: int) -> list:
    update_logs = []

    for stack in stacks:
        if stack.get('EndpointId') != endpointId:
            continue

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
        
    return update_logs

#
## Script Start point
#
def main():
    global CONFIGS
    
    load_configs()
    check_portainer_availability()
    
    pprint('INF', 'Obtaining portainer instance information')
    infrastructure = get_instance_data()
    pprint('ACT', f'Found {len(infrastructure[0])} endpoints [No. of stacks: {len(infrastructure[1])}]')

    disabled_endpoints = (str(CONFIGS.get('SKIP_ENDPOINTS_LIST')).split(','))

    for endpoint in infrastructure[0]:
        if endpoint.get("EndpointName") in disabled_endpoints:
            pprint('WRN', 'Found endpoint is present in the exclusion list, skipping')
            continue

        pprint('INF', f'Updating stacks on endpoint {endpoint.get("EndpointName")}')
        statuses = update_stack_containers(stacks=infrastructure[1], endpointId=endpoint.get('EndpointId'))
        for status in statuses:
            if status.get('RedeployStatus') == 200:
                pprint('ACT', f"Stack no. {status.get('StackId')} updated successfully")
            else:
                pprint('ERR', f"Stack no. {status.get('StackId')} failed to update")
    
    print(F'\n{F.LIGHTMAGENTA_EX}Part of sysadmin-scripts Github Repository [https://github.com/unkn0wnAPI/sysadmin-scripts]{S.RESET_ALL}\n')


if __name__ == "__main__":
    main()
