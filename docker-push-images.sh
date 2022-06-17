# Only of interest for kubernetes.

python3 balancer/nginix_configs/create_config.py kube
docker-compose build
docker tag balancer:latest tomashq98/wdm:balancer
docker push tomashq98/wdm:balancer
docker tag order-nodes-1:latest tomashq98/wdm:order-nodes-1
docker push tomashq98/wdm:order-nodes-1
docker tag payment-nodes-1:latest tomashq98/wdm:payment-nodes-1
docker push tomashq98/wdm:payment-nodes-1
docker tag stock-nodes-1:latest tomashq98/wdm:stock-nodes-1
docker push tomashq98/wdm:stock-nodes-1
docker tag order-coord-1:latest tomashq98/wdm:order-coord-1
docker push tomashq98/wdm:order-coord-1
docker tag payment-coord-1:latest tomashq98/wdm:payment-coord-1
docker push tomashq98/wdm:payment-coord-1
docker tag stock-coord-1:latest tomashq98/wdm:stock-coord-1
docker push tomashq98/wdm:stock-coord-1

# This way we assure that the localhost copy contains the right IP addresses.
python3 balancer/nginix_configs/create_config.py 
