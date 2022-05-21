pip3 install -r requirements.txt 
cd ipv4checksum && pip3 install .
cd ..
cd ..
python3 app.py $1 $2 &

if [ $# -eq 2 ]; then
    python3 inter_com.py $1 $2 &
fi

