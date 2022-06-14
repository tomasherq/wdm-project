import yaml
from collections import defaultdict
import json


def pretty_print(object):
    print(json.dumps(object, indent=4))


def increaseHostPort(index):
    hostPorts[index] += 1


def add_balancer(coordinator_names, ip_address, docker_object):

    docker_object["services"]["balancer"] = {"build": "./balancer",
                                             "ports": ["1101:80"],
                                             "depends_on": coordinator_names,
                                             "networks": {"shared_net": {"ipv4_address": ip_address}}}

    return docker_object


docker_object = {"version": "3", "services": {}}

addresses = defaultdict(list)
hostPorts = [1102, 8080]
template = ""
with open("../env/addresses.env") as file:
    for line in file:
        if line.strip():
            data_line = line.split("=")

            if "PREFIX_IP" == data_line[0]:
                PREFIX_IP = data_line[1].strip()
            else:
                addresses[data_line[0]] = data_line[1].strip().split(";")


docker_object["networks"] = {"shared_net": {"driver": "bridge", "ipam": {"config": [{"subnet": f"{PREFIX_IP}.0/24"}]}}}
with open('templates/node_standard.yaml', 'r') as file:
    template = yaml.safe_load(file)

coordinator_names = list()
for nodeType in addresses:

    cont = 1
    for address in addresses[nodeType]:

        if "BALANCER" in nodeType:
            docker_object = add_balancer(coordinator_names, f'{PREFIX_IP}.{address}', docker_object)
            break

        service = nodeType.split("_")[0].lower()
        dockerFile = "Mongo.Dockerfile"
        instanceType = nodeType.split("_")[1].lower()
        command = f'bash -c "cd {service}/common/ && bash setup_ssh.sh && bash execution.sh {cont} "'
        ports = [f"{hostPorts[0]}:2801"]

        increaseHostPort(0)
        hostname = f'{service}-{instanceType.lower()}-{cont}'

        if "COORD" in nodeType:
            # This is a bit confusing, but it works
            instanceType = service.upper()
            service = "coordinator"
            dockerFile = "coordinator.Dockerfile"
            command = f'bash -c "cd {service}/common/ && bash execution.sh {cont} {instanceType}"'
            ports.append(f"{hostPorts[1]}:2802")

            coordinator_names.append(hostname)

            increaseHostPort(1)

        volumes = [f'./{service}:/app/{service}', f'./common:/app/{service}/common']
        ipAddress = f'{PREFIX_IP}.{address}'

        nodeInfo = template["hostname"].copy()
        nodeInfo["container_name"] = hostname

        nodeInfo["build"] = template["hostname"]["build"].copy()
        nodeInfo["build"]["dockerfile"] = dockerFile

        nodeInfo["image"] = hostname
        nodeInfo["hostname"] = hostname
        nodeInfo["volumes"] = volumes
        nodeInfo["command"] = command
        nodeInfo["ports"] = ports

        nodeInfo["networks"] = {"shared_net": {"ipv4_address": ipAddress}}

        docker_object["services"][hostname] = nodeInfo

        cont += 1


with open('../docker-compose.yml', 'w') as yaml_file:
    data = json.dumps(docker_object, indent=4)
    yaml.dump(json.loads(data), yaml_file, indent=4, default_flow_style=False, sort_keys=False)
