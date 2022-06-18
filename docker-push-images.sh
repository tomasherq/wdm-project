python3 balancer/nginix_configs/create_config.py kube
docker-compose build
docker tag balancer:latest tomashq98/wdm:balancer
docker push tomashq98/wdm:balancer
docker tag order-nodes-1:latest tomashq98/wdm:order-nodes-1
docker push tomashq98/wdm:order-nodes-1
docker tag order-nodes-2:latest tomashq98/wdm:order-nodes-2
docker push tomashq98/wdm:order-nodes-2
docker tag order-nodes-3:latest tomashq98/wdm:order-nodes-3
docker push tomashq98/wdm:order-nodes-3
docker tag payment-nodes-1:latest tomashq98/wdm:payment-nodes-1
docker push tomashq98/wdm:payment-nodes-1
docker tag payment-nodes-2:latest tomashq98/wdm:payment-nodes-2
docker push tomashq98/wdm:payment-nodes-2
docker tag payment-nodes-3:latest tomashq98/wdm:payment-nodes-3
docker push tomashq98/wdm:payment-nodes-3
docker tag stock-nodes-1:latest tomashq98/wdm:stock-nodes-1
docker push tomashq98/wdm:stock-nodes-1
docker tag stock-nodes-2:latest tomashq98/wdm:stock-nodes-2
docker push tomashq98/wdm:stock-nodes-2
docker tag stock-nodes-3:latest tomashq98/wdm:stock-nodes-3
docker push tomashq98/wdm:stock-nodes-3
docker tag order-coord-1:latest tomashq98/wdm:order-coord-1
docker push tomashq98/wdm:order-coord-1
docker tag order-coord-2:latest tomashq98/wdm:order-coord-2
docker push tomashq98/wdm:order-coord-2
docker tag payment-coord-1:latest tomashq98/wdm:payment-coord-1
docker push tomashq98/wdm:payment-coord-1
docker tag payment-coord-2:latest tomashq98/wdm:payment-coord-2
docker push tomashq98/wdm:payment-coord-2
docker tag stock-coord-1:latest tomashq98/wdm:stock-coord-1
docker push tomashq98/wdm:stock-coord-1
docker tag stock-coord-2:latest tomashq98/wdm:stock-coord-2
docker push tomashq98/wdm:stock-coord-2
python3 balancer/nginix_configs/create_config.py
