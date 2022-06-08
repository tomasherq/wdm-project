#!/bin/bash




path_dir="/app/common/restored_files/$1/$2"

while :
do
    if [ -d $path_dir ] 
    then
        mongorestore $path_dir
        break
    else
        sleep 2
    fi
done