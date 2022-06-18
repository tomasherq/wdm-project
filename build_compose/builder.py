import yaml
from collections import defaultdict
import json

'''This file creates the ../docker-compose.yml file'''


# This can be changed to another location
DOCKER_REPO = "tomashq98/wdm"


def increaseHostPort(index):
    hostPorts[index] += 1


def add_balancer(coordinator_names, ip_address, docker_object):

    docker_object["services"]["balancer"] = {"build": "./balancer",
                                             "image": "balancer",
                                             "ports": ["1101:80"],
                                             "depends_on": coordinator_names,
                                             "networks": {"shared-net": {"ipv4_address": ip_address}}}

    return docker_object


def add_command_file(image_list):

    tag_command_template = f"""docker tag ##name##:latest {DOCKER_REPO}:##name##\ndocker push {DOCKER_REPO}:##name##\n"""

    text = ''
    for image_name in image_list:
        text += tag_command_template.replace("##name##", image_name)

    with open("docker-push-images.sh", "w") as file_push_dock:
        file_push_dock.write("python3 balancer/nginix_configs/create_config.py kube\n")

        file_push_dock.write("docker-compose build\n")
        file_push_dock.write(text)
        file_push_dock.write("python3 balancer/nginix_configs/create_config.py\n")


docker_object = {"version": "3", "services": {}}

addresses = defaultdict(list)
hostPorts = [1102, 8880]
template = ""
with open("env/addresses.env") as file:
    for line in file:

        if line.strip():
            data_line = line.split("=")

            if "KUBERNETES" in line:
                continue

            if "PREFIX_IP" == data_line[0]:
                PREFIX_IP = data_line[1].strip()
            else:
                addresses[data_line[0]] = data_line[1].strip().split(";")


docker_object["networks"] = {"shared-net": {"driver": "bridge", "ipam": {"config": [{"subnet": f"{PREFIX_IP}.0/24"}]}}}
with open('build_compose/templates/node_standard.yaml', 'r') as file:
    template = yaml.safe_load(file)

coordinator_names = list()
image_list = ["balancer"]
for nodeType in addresses:

    cont = 1
    for address in addresses[nodeType]:

        if "BALANCER" in nodeType:
            docker_object = add_balancer(coordinator_names, f'{PREFIX_IP}.{address}', docker_object)
            break

        service = nodeType.split("_")[0].lower()

        dockerFile = f"{service}.Dockerfile"
        instanceType = nodeType.split("_")[1].lower()
        command = f'bash -c "bash /app/common/setup_ssh.sh && bash /app/common/execution.sh {cont} "'
        ports = [f"{hostPorts[0]}:2801"]

        increaseHostPort(0)
        hostname = f'{service}-{instanceType.lower()}-{cont}'

        image_list.append(hostname)

        if "COORD" in nodeType:
            # This is a bit confusing, but it works
            instanceType = service.upper()
            service = "coordinator"
            dockerFile = "coordinator.Dockerfile"
            command = f'bash -c "bash /app/common/execution.sh {cont} {instanceType}"'
            ports.append(f"{hostPorts[1]}:2802")

            coordinator_names.append(hostname)

            increaseHostPort(1)

        ipAddress = f'{PREFIX_IP}.{address}'

        nodeInfo = template["hostname"].copy()
        nodeInfo["container_name"] = hostname

        nodeInfo["build"] = template["hostname"]["build"].copy()
        nodeInfo["build"]["dockerfile"] = dockerFile

        nodeInfo["image"] = hostname
        nodeInfo["hostname"] = hostname
        nodeInfo["command"] = command
        nodeInfo["ports"] = ports

        nodeInfo["networks"] = {"shared-net": {"ipv4_address": ipAddress}}

        docker_object["services"][hostname] = nodeInfo

        cont += 1


add_command_file(image_list)

with open('docker-compose.yml', 'w') as yaml_file:
    data = json.dumps(docker_object, indent=4)
    yaml.dump(json.loads(data), yaml_file, indent=4, default_flow_style=False, sort_keys=False)
