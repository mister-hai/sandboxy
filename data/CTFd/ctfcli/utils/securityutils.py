# Firewall rules for visible challenges
# with google cloud
import os
import json
import os
import tempfile
import subprocess
from pathlib import Path

from collections import namedtuple
from urllib.parse import urlparse


def firewall(visible, hidden):
    """
    NOT IMPLEMENTED YET
    turn visible into ON
    turn hidden into OFF
        
    FIRST PARAM shall be state to set firewall to
    SECOND PARAM shall be the challenge to generate a firewall rule for
    """
    rules = os.popen('gcloud compute firewall-rules --format=json list').read()
    for category in visible:
        for challenge in visible[category]:
            if challenge['port'] and challenge['name'] not in rules:
                os.system(
                    f"""
                        gcloud compute firewall-rules create {challenge['name']} \
                            --allow tcp:{challenge['port']} \
                            --priority 1000 \
                            --target-tags challs
                    """
                )
                print('Created firewall rules for:')
                print(challenge['name'])    
    for category in hidden:
        for challenge in hidden[category]:
            if challenge['port'] and challenge['name'] in rules:
                os.system(
                    f"""
                        echo -e "Y\n" | gcloud compute firewall-rules delete {challenge['name']}
                    """)
                print('Deleted firewall rules for:')
                print(challenge['name'])


def sanitize_name(name):
    """
    Function to sanitize names to docker safe image names
    TODO: Good enough but probably needs to be more conformant with docker
    """
    return name.lower().replace(" ", "-")


def build_image(challenge):
    name = sanitize_name(challenge["name"])
    path = Path(challenge.file_path).parent.absolute()
    print(f"Building {name} from {path}")
    subprocess.call(["docker", "build", "-t", name, "."], cwd=path)
    return name

def export_image(challenge):
    name = sanitize_name(challenge["name"])
    temp = tempfile.NamedTemporaryFile(delete=False, suffix=f"_{name}.docker.tar")
    subprocess.call(["docker", "save", "--output", temp.name, name])
    return temp.name

def get_exposed_ports(challenge):
    image_name = sanitize_name(challenge["name"])
    output = subprocess.check_output(
        ["docker", "inspect", "--format={{json .Config.ExposedPorts }}", image_name,]
    )
    output = json.loads(output)
    if output:
        ports = list(output.keys())
        if ports:
            # Split '2323/tcp'
            port = ports[0]
            port = port.split("/")
            port = port[0]
            return port
        else:
            return None
    else:
        return None

        
Prompt = namedtuple("Prompt", ["text", "type", "default", "required", "multiple"])


def ssh(challenge, host):
    # Build image
    image_name = build_image(challenge=challenge)
    print(f"Built {image_name}")

    # Export image to a file
    image_path = export_image(challenge=challenge)
    print(f"Exported {image_name} to {image_path}")
    filename = Path(image_path).name

    # Transfer file to SSH host
    print(f"Transferring {image_path} to {host}")
    host = urlparse(host)
    folder = host.path or "/tmp"
    target_file = f"{folder}/{filename}"
    exposed_port = get_exposed_ports(challenge=challenge)
    domain = host.netloc[host.netloc.find("@") + 1 :]
    subprocess.run(["scp", image_path, f"{host.netloc}:{target_file}"])
    subprocess.run(["ssh", host.netloc, f"docker load -i {target_file} && rm {target_file}"])
    subprocess.run(["ssh",host.netloc,f"docker run -d -p{exposed_port}:{exposed_port} {image_name}"])

    # Clean up files
    os.remove(image_path)
    print(f"Cleaned up {image_path}")
    return True, domain, exposed_port


def registry(challenge, host):
    # Build image
    image_name = build_image(challenge=challenge)
    print(f"Built {image_name}")
    url = urlparse(host)
    tag = f"{url.netloc}{url.path}"
    subprocess.call(["docker", "tag", image_name, tag])
    subprocess.call(["docker", "push", tag])

DEPLOY_HANDLERS = {"ssh": ssh, "registry": registry}
