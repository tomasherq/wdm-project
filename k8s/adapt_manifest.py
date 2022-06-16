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

    with open(f"k8s/{filename}", "w") as file_write:

        file_write.write(new_manifest)
