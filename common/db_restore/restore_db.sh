#!/bin/bash



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