#!/bin/bash

#
## Script Name: docker-compose Utilities
## Author:      unkn0wnAPI [github.com/unkn0wnAPI]
## Information: Automates certain docker-compose actions
#

#
## Configuration
#
DOCKER_CONFIG_PATH="" # Sets the parent directory of the docker-compose.yml file

#
## Functions
#
_dockerRestart () {
	current_dir=$PWD;
	cd $DOCKER_CONFIG_PATH;
	docker-compose restart;
	cd $current_dir;
}

_dockerStop () {
	current_dir=$PWD;
	cd $DOCKER_CONFIG_PATH;
	docker-compose down;
	cd $current_dir;
}

_dockerStart () {
	current_dir=$PWD;
	cd $DOCKER_CONFIG_PATH;
	docker-compose up -d;
	cd $current_dir;
}

_dockerUpdate () {
	current_dir=$PWD;
	cd $DOCKER_CONFIG_PATH;
	docker-compose pull;
	docker-compose down;
	docker image prune -f;
	docker-compose up -d;
	cd $current_dir;
}

#
## Script Start point
#
if [ "$#" -lt 1 ]; then
  echo >&2 "[ERROR] Missing arguments"
  echo >&2 "Syntax -> ./dockerUtils.sh [Mode]"
  echo >&2 "Available Modes: restart, start, stop, update"
  exit 1
fi

if [ "$1" == "restart" ]; then
	echo >&2 "[SCRIPT] Restarting docker containers"
    _dockerRestart
	exit 0
elif [ "$1" == "stop" ]; then
    echo >&2 "[SCRIPT] Stopping docker containers"
    _dockerStop
	exit 0
elif [ "$1" == "start" ]; then
    echo >&2 "[SCRIPT] Starting docker containers"
    _dockerStart
    exit 0
elif [ "$1" == "update" ]; then
    echo >&2 "[SCRIPT] Updating and restarting docker containers"
    _dockerUpdate
    exit 0
else
    echo >&2 "[ERROR] Unsupported argument passed"
    exit 1
fi
