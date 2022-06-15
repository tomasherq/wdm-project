from collections import defaultdict

PREFIX_IP = ''
CONFIG_INFO = ''

with open("nginix_configs/template_config.conf", "r") as file_read:
    CONFIG_INFO = file_read.read()

addresses = defaultdict(list)
TEMPLATE_SERVER = "\t server ##IP_ADDRESS##:2801 weight=5; \n"
with open("../env/addresses.env") as file:
    for line in file:
        if line.strip():
            data_line = line.split("=")
            if "PREFIX_IP" == data_line[0]:
                PREFIX_IP = data_line[1].strip()
            else:
                addresses[data_line[0]] = data_line[1].strip().split(";")

for address_type in addresses:
    if "COORD" in address_type:
        lines_replace = ""
        for address in addresses[address_type]:
            full_address = PREFIX_IP+"."+address
            lines_replace += TEMPLATE_SERVER.replace("##IP_ADDRESS##", full_address)
        CONFIG_INFO = CONFIG_INFO.replace(address_type, lines_replace[:-1])


with open("nginx.conf", "w") as file_write:
    file_write.write(CONFIG_INFO)
