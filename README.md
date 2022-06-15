# Web-scale Data Management Project

This project implements a set of microservices for a shopping cart.

### Technologies used
* `python`
* `Flask`
* `mongoDB`
* `docker`
* `docker-compose`
* `nginix`
* `kubernetes`

### Project structure

* `balancer`
    Folder containing `nginix` configuration for load balancing between the coordinators

* `build_compose`
    Folder containing configuration for the docker-compose deployment
    
* `common` 
    Folder containing common files shared between services and coordinators

* `coordinator`
    Implementation of the coordinators

* `env`
    Folder containing the Redis env variables for the docker-compose deployment

* `k8s`
    Folder containing the kubernetes deployments, apps and services for the ingress, order, payment and stock services.

* `order`
    Folder containing the order application logic and dockerfile. 
    
* `payment`
    Folder containing the payment application logic and dockerfile. 

* `stock`
    Folder containing the stock application logic and dockerfile. 

* `test`
    Folder containing some basic correctness tests for the entire system.


### Deployment types:

#### docker-compose (local development)

After coding the REST endpoint logic run `docker-compose up --build` in the base folder to test if your logic is correct
(you can use the provided tests in the `\test` folder and change them as you wish). 

***Requirements:*** You need to have docker and docker-compose installed on your machine.

#### minikube (local k8s cluster)

This setup is for local k8s testing to see if your k8s config works before deploying to the cloud. 
First deploy your database using helm by running the `deploy-charts-minicube.sh` file (in this example the DB is Redis 
but you can find any database you want in https://artifacthub.io/ and adapt the script). Then adapt the k8s configuration files in the
`\k8s` folder to mach your system and then run `kubectl apply -f .` in the k8s folder. 

***Requirements:*** You need to have minikube (with ingress enabled) and helm installed on your machine.

#### kubernetes cluster (managed k8s cluster in the cloud)

Similarly to the `minikube` deployment but run the `deploy-charts-cluster.sh` in the helm step to also install an ingress to the cluster. 

***Requirements:*** You need to have access to kubectl of a k8s cluster.

### Evaluation:

#### Scalability 

The system design allows us to add as many nodes as we want. Each set of nodes will have a coordinator and the load between the coordinators and the nodes is equally distributed.

#### Consistency 

To ensure consistency we hash every database. The hashes of the multiple instances of a database are compared. If at least one of them is different from the others, then there is an inconsistency. To restore from the inconsistencies, we find the most common hash and we assume that the databases with the most common hash are consistent, so the rest have to be restored. If there is not a common hash in between the databases, then we check which database was last updated and we assume that this is the consistent one. Once we have a list of the inconsistent and inconsistent databases, we choose a consistent database to dump their data. Then, this data is used to update the inconsistent ones.

#### Availability 

For each service there are multiple coordinators and nodes. The load between the coordinators is balanced by a load balancer. For this purpose we use `nginix`. Hence, a request is first directed to the load balancer, which decides to which coordinator it is going to be sent. The coordinator hashes the request and forwards it to one of the nodes. If the request is a write, this node also forwards the request to the rest of the nodes. If the request is a read, nothing else is needed to be done.

#### Fault Tolerance 

Suppose node A is forwarding a request to the rest of the nodes. Suppose also that one of these nodes is down, let's say node B.
In that case, the request that is sent by node A to node B returns a time-out and, hence, node A is aware of the node B being down. Then, node A informs the coordinator that node B is down and the coordinator removes node B from the list of nodes. IN this way, we reassure that the response time remains short and we avoid reduced availability of the service. The coordinator checks regularly if  node B is up again. Once it is up it informs all the other nodes.


#### Transaction Performance
throughput, latency, efficiency results here

#### Event-Driven Design

The requests from a node to the rest of the nodes are done asynchronously. In this way the node sending the request doesn't have to wait for the reply before forwarding this request to the next node.