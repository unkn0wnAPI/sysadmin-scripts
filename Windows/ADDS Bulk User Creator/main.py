#
## Script Name: ADDS Bulk User Creator
## Author:      unkn0wnAPI [https://github.com/unkn0wnAPI]
## Information: Creates script to add/remove users from Windows Server Active Directory (Tested on Windows Server 2016)
#

#
## Imports
#
import re

#
## Configuration
#
USER_LIST_FNAME = "names.txt" # Specifies input file with users full names
OUTPUT_ADD_SCRIPT_FNAME = "ADDS_add_users.bat" # Specifies output user add script name
OUTPUT_REM_SCRIPT_FNAME = "ADDS_rem_users.bat" # Specifies output user remove script name
FIRST_LOGON_PASSWD = "" # Specifies temp password for first time logon to AD DS
USER_COMMENT = "" # Specifies comment for users created using this script
NAME_FIRST = True # Change this according to names.txt syntax [Name Surname => True, Surname Name => False]
USE_COLORS_IN_OUTPUT = False # Enable rich-color output
GEN_REMOVE_SCRIPT = False # Enable creation of a 'reverse' script, which removes all generated users | OPTIONAL

#
## Functions
#
def rem_accents(string): # Removes polish accents from login names
    new = string.lower()
    new = re.sub(r'[ą]', 'a', new)
    new = re.sub(r'[ę]', 'e', new)
    new = re.sub(r'[ł]', 'l', new)
    new = re.sub(r'[ó]', 'o', new)
    new = re.sub(r'[ć]', 'c', new)
    new = re.sub(r'[ś]', 's', new)
    new = re.sub(r'[ż]', 'z', new)
    new = re.sub(r'[ź]', 'z', new)
    return new

#
## Script Parameters Initialization
#
if(USE_COLORS_IN_OUTPUT):
    GREENC =  '\033[32m' 
    BLUEC =  '\033[36m' 
    REDC =  '\033[31m' 
    ENDC = '\033[m' 
else:
    GREENC = ''
    BLUEC = ''
    REDC = ''
    ENDC = ''

try:
    USER_LIST = open(USER_LIST_FNAME,'r', encoding="utf-8") # Read user defines users list
except FileNotFoundError:
    print(REDC + f"[ERROR] - FileNotFoundError detected! Before running the script, check if {USER_LIST_FNAME} exists in working directory" + ENDC)
    exit()

OUTPUT_ADD_SCRIPT = open(OUTPUT_ADD_SCRIPT_FNAME, 'w', encoding="utf-8") # Start write routine for AD_add_users script

try:
    USERS = USER_LIST.read().splitlines()
except UnicodeDecodeError:
    print(REDC + f"[ERROR] - UnicodeDecodeError detected! File containing data for user creation {USER_LIST_FNAME} might contain non utf-8 chars. Before running the script check encoding options" + ENDC)
    exit()
    
USER_LIST.close()

#
## Script Start point
#
def main():
    print(GREENC + f"[INFO] - Starting Script" + ENDC)
    OUTPUT_ADD_SCRIPT.write(f"chcp 65001") # Enables UTF-8 support in cmd
    OUTPUT_ADD_SCRIPT.write("\n")
    for user in USERS:
        if(NAME_FIRST):
            user = user.strip()
            try:
                name, surname = user.split(' ')
            except ValueError:
                print(REDC + f"[ERROR] - ValueError detected! If possible delete all unnecessary empty new lines in {USER_LIST_FNAME}" + ENDC)
                exit()
            login_name = name[0] + surname
        else:
            user = user.strip()
            try:
                surname, name = user.split(' ')
            except ValueError:
                print(REDC + f"[ERROR] - ValueError detected! If possible delete all unnecessary empty new lines in {USER_LIST_FNAME}" + ENDC)
                exit()
            login_name = name[0] + surname
        print(BLUEC + f"[CREATE] - net user /ADD {rem_accents(login_name)} {FIRST_LOGON_PASSWD} /FULLNAME:\"{user}\" /COMMENT:\"{USER_COMMENT}\" /ACTIVE:Yes /LOGONPASSWORDCHG:Yes /DOMAIN" + ENDC)
        OUTPUT_ADD_SCRIPT.write(f"net user /ADD {rem_accents(login_name)} {FIRST_LOGON_PASSWD} /FULLNAME:\"{user}\" /COMMENT:\"{USER_COMMENT}\" /ACTIVE:Yes /LOGONPASSWORDCHG:Yes /DOMAIN")
        OUTPUT_ADD_SCRIPT.write("\n")
    OUTPUT_ADD_SCRIPT.write("pause")
    OUTPUT_ADD_SCRIPT.close()
    if(GEN_REMOVE_SCRIPT): 
        OUTPUT_REM_SCRIPT = open(OUTPUT_REM_SCRIPT_FNAME, 'w', encoding="utf-8")
        OUTPUT_REM_SCRIPT.write(f"chcp 65001") # Enables UTF-8 support in cmd
        OUTPUT_REM_SCRIPT.write("\n")
        for user in USERS:
            if(NAME_FIRST):
                user = user.strip()
                try:
                    name, surname = user.split(' ')
                except ValueError:
                    print(REDC + f"[ERROR] - ValueError detected! If possible delete all unnecessary empty new lines in {USER_LIST_FNAME}" + ENDC)
                    exit()
                login_name = name[0] + surname
            else:
                user = user.strip()
                try:
                    surname, name = user.split(' ')
                except ValueError:
                    print(REDC + f"[ERROR] - ValueError detected! If possible delete all unnecessary empty new lines in {USER_LIST_FNAME}" + ENDC)
                    exit()
                login_name = name[0] + surname
            OUTPUT_REM_SCRIPT.write(f"net user {rem_accents(login_name)} /DELETE")
            OUTPUT_REM_SCRIPT.write("\n")
        OUTPUT_REM_SCRIPT.write("pause")
        OUTPUT_REM_SCRIPT.close()
        print(GREENC + f"[INFO] - Generated additional script [{OUTPUT_REM_SCRIPT.name}]" + ENDC)
    print(GREENC + f"[INFO] - Operation was executed successfully [Saved data to {OUTPUT_ADD_SCRIPT.name}]" + ENDC)
    print(GREENC + f"[INFO] - To add users to domain, run {OUTPUT_ADD_SCRIPT.name} with Administrator privileges" + ENDC)

if __name__ == "__main__":
    main()