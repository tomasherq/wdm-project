pip3 install -r requirements.txt 

sleep 0.5
cd ipv4checksum && pip3 install .
cd ..
cd ..


if [ $# -eq 2 ]; then
    python3 app.py $1 $2 &
    python3 inter_com.py $1 $2 
else
    # Maybe we can enable logging, no idea
    mongod > /dev/null & 
fi


python3 app.py $1 $2