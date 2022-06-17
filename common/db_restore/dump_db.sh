#!/bin/bash

# This file is used to dump the database of a consistent node to a file
# The file with the consistent database is then used to restore 
# the database of the inconsistent ones

# $1 is the service of the directory
# $2 is the id is given by the server
# $3 is a list of the nodes given by the server separated by ";"

DIRECTORY_DUMP="/tmp/$1/$2"

FILE_LOCATION="$DIRECTORY_DUMP/$1s/$1.bson"

SEND_LOCATION="/tmp/$1_$2.bson"

mkdir -p /app/$1/common/db_restore/restored_files/$1/

rm -r -f /app/$1/common/db_restore/restored_files/$1/*

mongodump -o $DIRECTORY_DUMP

IFS=';' read -ra ip_list <<< "$3"

# Print the split string
for ip_add in "${ip_list[@]}"
do    
    scp -o "StrictHostKeyChecking no" -i /home/sender/.ssh/sender_key $FILE_LOCATION sender@$ip_add:$SEND_LOCATION 
done

rm $FILE_LOCATION