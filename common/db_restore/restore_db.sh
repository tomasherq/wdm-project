#!/bin/bash



FILE_LOCATION="/app/$1/common/db_restore/restored_files/$1s/$1.bson"


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