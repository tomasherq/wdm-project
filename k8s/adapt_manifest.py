import os
DOCKER_REPO = "tomashq98/wdm"


for filename in os.listdir("k8s"):
    if ".py" in filename:
        continue

    with open(f"k8s/{filename}", "r") as file_read:

        full_text = file_read.read()

    new_manifest = full_text
    for line in full_text.split("\n"):

        if "image:" in line:

            image_name = line.split("image: ")[1].strip()
            new_image_name = DOCKER_REPO+":"+image_name

            new_line = line.replace(image_name, new_image_name)
            new_manifest = new_manifest.replace(line, new_line)

        if "service" in filename:
            if "port:" in line:
                port_number = line.strip().split("port:")[1].strip()
                new_port = port_number
                if "1" == port_number[0]:

                    new_port = "2801"
                    if "balancer" in filename:
                        new_port = "80"
                elif "8" == port_number[0]:
                    new_port = "2802"
                new_line = line.replace(port_number, new_port)
                new_manifest = new_manifest.replace(line, new_line)

    if "env-addresses" in filename:
        new_manifest = new_manifest.replace('KUBERNETES: "0"', 'KUBERNETES: "1"')

    with open(f"k8s/{filename}", "w") as file_write:

        file_write.write(new_manifest)
