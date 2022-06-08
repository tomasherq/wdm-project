#!/bin/bash
# $1 is the service of the directory and $2 is the id is given by the server

mkdir -p /app/$1/common/db_restore/restored_files/$1/

rm -r -f /app/$1/common/db_restore/restored_files/$1/*

mongodump -o /app/$1/common/db_restore/restored_files/$1/$2



