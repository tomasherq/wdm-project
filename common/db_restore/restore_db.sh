#!/bin/bash

# This file is used to restore the inconsistent databases 
# It uses the file with the correct database as created by the 
# dump_db.sh

FILE_LOCATION="/tmp/$1_$2.bson"

while :
do
    if [ -d $FILE_LOCATION ] 
    then
        mongorestore $FILE_LOCATION
        break
    else
        sleep 2
    fi
done

rm $FILE_LOCATION