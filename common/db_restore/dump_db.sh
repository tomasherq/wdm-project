#!/bin/bash
# $2 is the service of the directory and $3 is the id is given by the server

mkdir -p /app/$1/common/db_restore/restored_files/$1/

rm -r /app/$1/common/db_restore/restored_files/$1/*

mongodump -o /app/$1/common/db_restore/restored_files/$1/$2



