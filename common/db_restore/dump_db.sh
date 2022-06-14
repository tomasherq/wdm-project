#!/bin/bash
# $1 is the service of the directory and $2 is the id is given by the server

DIRECTORY_DUMP="/tmp/$1/$2"

FILE_LOCATION="$DIRECTORY_DUMP/$1s/$1.bson"

SEND_LOCATION="/tmp/$1_$2.bson"

mkdir -p /app/$1/common/db_restore/restored_files/$1/

rm -r /app/$1/common/db_restore/restored_files/$1/*

mongodump -o $DIRECTORY_DUMP

# $3 is a list of the nodes given by the server separated by 192.168.124.10;

IFS=';' read -ra ip_list <<< "$3"

#Print the split string
for ip_add in "${ip_list[@]}"
do

    # echo "$DIRECTORY_DUMP sender@$ip_add:$DIRECTORY_DUMP -i /home/sender/.ssh/sender_key"
    
    # This will not work locally
    scp -o "StrictHostKeyChecking no" -i /home/sender/.ssh/sender_key $FILE_LOCATION sender@$ip_add:$SEND_LOCATION 
done

rm $FILE_LOCATION