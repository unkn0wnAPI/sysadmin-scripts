# ADDS Bulk User Creator

This is a script written in Python, that creates ADDS Users batch script based on data provided by the user.

## Getting Started

The scripts requires specific software and/or packages (See [Prerequisites](#prerequisites) for more information).

### Prerequisites

Tools and elements required to successfully use the script:

* Windows Server (with ADDS installed and configured);
* Windows (or Linux) machine which will generate the batch script;
* [Python 3](https://www.python.org/) installed on the machine used for generation.

## Configuration

The script is semi-configurable, this means you are able to modify certain aspects of the script.

| Option name               | Description                                               | Value Type    |
| ------------------------- | --------------------------------------------------------- | ------------- |
| USER_LIST_FNAME           | Sets the file name with names and surnames                | String        |
| OUTPUT_ADD_SCRIPT_FNAME   | Sets name for the `add user` batch script                 | String        |
| OUTPUT_REM_SCRIPT_FNAME   | Sets name for the `rem user` batch script                 | String        |
| FIRST_LOGON_PASSWD        | Sets account first log-in password                        | String        |
| USER_COMMENT              | Sets the comment that will be added to user account       | String        |
| NAME_FIRST                | Reverses the order of data read from `USER_LIST_FNAME`    | Boolean       |
| USE_COLORS_IN_OUTPUT      | Enables rich-color terminal output                        | Boolean       |
| GEN_REMOVE_SCRIPT         | Enables the creation of `rem user` batch script           | Boolean       |

## Explanation + Example

The script works by reading data from `USER_LIST_FNAME` and using it as the user's name, surname and account login.  

For example if the contents of the `USER_LIST_FNAME` is:

```txt
Dean James
Richard Smith
```

The script will treat 1st line element as surname and 2nd element as name on (You can change this behavior by setting `NAME_FIRST` to `true`).

Which will result in creation of the following accounts:

```txt
jdean [Name: James, Surname: Dean]
rsmith [Name: Richard, Surname: Smith]
```

Disclaimer: **IT IS IMPORTANT THAT AT THIS TIME, THE SCRIPT WON'T WORK IF SOMEONE IS USING TWO NAMES/SURNAMES**

## Usage

To run this script you need to issue the following commands in the directory with `names.txt` present:

```properties
# On windows
python main.py

# On Linux/Unix based systems
python3 main.py
```
