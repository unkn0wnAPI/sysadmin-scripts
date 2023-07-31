#!/bin/bash

#
## Script Name: Git Repositories Auto Sync
## Author:      unkn0wnAPI [github.com/unkn0wnAPI]
## Information: Allows to sync git repositories manually or automatically (using cronjob)
#

#
## Configuration
#
REPOS_PARENT_FOLDER='' # Sets parent dir of Git repositories

#
## Functions
#
_gitOperations(){
    echo ----Syncing [$tempdir] with remote repository---- >> /tmp/ghSync_$(date +'%d-%m-%Y').log
    echo "---GIT FETCH---" >> /tmp/ghSync_$(date +'%d-%m-%Y').log
    git fetch >> /tmp/ghSync_$(date +'%d-%m-%Y').log
    echo "---GIT STATUS---" >> /tmp/ghSync_$(date +'%d-%m-%Y').log
    git status >> /tmp/ghSync_$(date +'%d-%m-%Y').log
    echo "---GIT PULL---" >> /tmp/ghSync_$(date +'%d-%m-%Y').log
    git pull >> /tmp/ghSync_$(date +'%d-%m-%Y').log
    echo "" >> /tmp/ghSync_$(date +'%d-%m-%Y').log
}

#
## Script Start point
#
echo "gitSync - Bash script to sync all github repos stored locally" > /tmp/ghSync_$(date +'%d-%m-%Y').log
sleep 10s
nc -z 8.8.8.8 53  >/dev/null 2>&1
IS_USER_ONLINE=$?
if [ $IS_USER_ONLINE -eq 0 ]; then
    CURRENT_DIR=$PWD
    for dir in "$REPOS_PARENT_FOLDER"/*
    do
        dir=${dir%*/}
        tempdir="$REPOS_PARENT_FOLDER/${dir##*/}"
        cd "$tempdir"
        _gitOperations
    done
    cd "$CURRENT_DIR"
else
    echo "[ERROR] NO INTERNET CONNECTION - Unable to sync repos!" >> /tmp/ghSync_$(date +'%d-%m-%Y').log
fi
