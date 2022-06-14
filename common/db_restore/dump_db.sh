#!/bin/bash
# $1 is the service of the directory and $2 is the id is given by the server

DIRECTORY_DUMP="/app/$1/common/db_restore/restored_files/$1/$2"

LOCATION_FILE="$DIRECTORY_DUMP/$1s/$1.bson"


mkdir -p /app/$1/common/db_restore/restored_files/$1/

rm -r -f /app/$1/common/db_restore/restored_files/$1/*

mongodump -o $DIRECTORY_DUMP

# $3 is a list of the nodes given by the server separated by 192.168.124.10;

IFS=';' read -ra ip_list <<< "$3"

for ip_add in "${ip_list[@]}"
do

    # This will not work locally
    scp -o "StrictHostKeyChecking no" -i /home/sender/.ssh/sender_key $LOCATION_FILE sender@$ip_add:$LOCATION_FILE 
done