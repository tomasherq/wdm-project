if [ $# -eq 2 ]; then
    python3 app.py $1 $2 &
    python3 inter_com.py $1 $2 
else
    chmod +x /app/common/db_restore/*
    # Maybe we can enable logging, no idea
    mongod > /dev/null & 
fi


python3 /app/app.py $1 $2