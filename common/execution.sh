pip3 install -r requirements.txt 
cd ipv4checksum && pip3 install .
cd ..
cd ..


if [ $# -eq 2 ]; then
    python3 app.py $1 $2 &
    python3 inter_com.py $1 $2 
fi


python3 app.py $1 $2