from collections import defaultdict
import sys

PREFIX_IP = ''
CONFIG_INFO = ''

with open("balancer/nginix_configs/template_config.conf", "r") as file_read:

    CONFIG_INFO = file_read.read()

addresses = defaultdict(list)
TEMPLATE_SERVER = "\t server ##IP_ADDRESS##:2801 weight=5; \n"

KUBERNETES = False
if len(sys.argv) > 1:

    KUBERNETES = sys.argv[1] == "kube"
with open("env/addresses.env") as file:

    file_data = file.read()
    new_data = file_data

    for line in file_data.split("\n"):
        if line.strip():
            data_line = line.split("=")

            if "PREFIX_IP" == data_line[0]:
                PREFIX_IP = data_line[1].strip()
            else:

                addresses[data_line[0]] = data_line[1].strip().split(";")


for address_type in addresses:

    if "COORD" in address_type:
        lines_replace = ""
        counter = 1
        for address in addresses[address_type]:
            full_address = PREFIX_IP+"."+address
            if KUBERNETES:
                full_address = "-".join(address_type.lower().split("_")[:-1])+"-"+str(counter)
                counter += 1
            lines_replace += TEMPLATE_SERVER.replace("##IP_ADDRESS##", full_address)

        CONFIG_INFO = CONFIG_INFO.replace(address_type, lines_replace[:-1])


with open("balancer/nginx.conf", "w") as file_write:
    file_write.write(CONFIG_INFO)
