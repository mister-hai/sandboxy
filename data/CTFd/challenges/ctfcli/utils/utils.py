
import getpass
from collections import namedtuple
from pathlib import Path
import os
import json
import tempfile
import subprocess
from pathlib import Path
from urllib.parse import urlparse

import yaml
import logging
import threading
import traceback
import subprocess
import pathlib
import sys
try:
    import colorama
    from colorama import init
    init()
    from colorama import Fore, Back, Style
    COLORMEQUALIFIED = True
except ImportError as derp:
    print("[-] NO COLOR PRINTING FUNCTIONS AVAILABLE, Install the Colorama Package from pip")
    COLORMEQUALIFIED = False

################################################################################
##############               LOGGING AND ERRORS                #################
################################################################################
LOGLEVEL            = 'DEV_IS_DUMB'
LOGLEVELS           = [1,2,3,'DEV_IS_DUMB']
log_file            = 'logfile'
logging.basicConfig(filename=log_file, format='%(asctime)s %(message)s', filemode='w')
logger              = logging.getLogger()
launchercwd         = pathlib.Path().absolute()


redprint          = lambda text: print(Fore.RED + ' ' +  text + ' ' + Style.RESET_ALL) if (COLORMEQUALIFIED == True) else print(text)
blueprint         = lambda text: print(Fore.BLUE + ' ' +  text + ' ' + Style.RESET_ALL) if (COLORMEQUALIFIED == True) else print(text)
greenprint        = lambda text: print(Fore.GREEN + ' ' +  text + ' ' + Style.RESET_ALL) if (COLORMEQUALIFIED == True) else print(text)
yellowboldprint = lambda text: print(Fore.YELLOW + Style.BRIGHT + ' {} '.format(text) + Style.RESET_ALL) if (COLORMEQUALIFIED == True) else print(text)
makeyellow        = lambda text: Fore.YELLOW + ' ' +  text + ' ' + Style.RESET_ALL if (COLORMEQUALIFIED == True) else text
makered           = lambda text: Fore.RED + ' ' +  text + ' ' + Style.RESET_ALL if (COLORMEQUALIFIED == True) else None
makegreen         = lambda text: Fore.GREEN + ' ' +  text + ' ' + Style.RESET_ALL if (COLORMEQUALIFIED == True) else None
makeblue          = lambda text: Fore.BLUE + ' ' +  text + ' ' + Style.RESET_ALL if (COLORMEQUALIFIED == True) else None
debuglog     = lambda message: logger.debug(message) 
infolog      = lambda message: logger.info(message)   
warninglog   = lambda message: logger.warning(message) 
errorlog     = lambda message: logger.error(message) 
criticallog  = lambda message: logger.critical(message)

################################################################################
##############             ERROR HANDLING FUNCTIONS            #################
################################################################################
def errorlogger(message):
    '''
    prints line number and traceback
    TODO: save stack trace to error log
            only print linenumber and function failure
    '''
    exc_type, exc_value, exc_tb = sys.exc_info()
    trace = traceback.TracebackException(exc_type, exc_value, exc_tb) 
    try:
        errormesg = message + ''.join(trace.format_exception_only())
        #traceback.format_list(trace.extract_tb(trace)[-1:])[-1]
        lineno = 'LINE NUMBER >>>' + str(exc_tb.tb_lineno)
        errorlog(lineno+errormesg)
    except Exception:
        print("EXCEPTION IN ERROR HANDLER!!!")
        print(message + ''.join(trace.format_exception_only()))

        
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

CTFd_API_v1 = ["/challenges",
              "/tags", 
              "/topics", 
              "/awards", 
              "/hints", 
              "/flags", 
              "/submissions", 
              "/scoreboard", 
              "/teams", 
              "/users", 
              "/statistics",
              "/files", 
              "/notifications", 
              "/configs", 
              "/pages", 
              "/unlocks", 
              "/tokens", 
              "/comments"]

CHALLENGE_SPEC_DOCS = {
    "name": Prompt(
        text="Challenge name or identifier",
        type=None,
        default=None,
        required=True,
        multiple=False,
    ),
    "author": Prompt(
        text="Your name or handle",
        type=None,
        default=getpass.getuser(),
        required=True,
        multiple=False,
    ),
    "category": Prompt(
        text="Challenge category",
        type=None,
        default=None,
        required=True,
        multiple=False,
    ),
    "description": Prompt(
        text="Challenge description shown to the user",
        type=None,
        default=None,
        required=True,
        multiple=False,
    ),
    "value": Prompt(
        text="How many points your challenge should be worth",
        type=int,
        default=None,
        required=True,
        multiple=False,
    ),
    "version": Prompt(
        text="What version of the challenge specification was used",
        type=None,
        default="0.1",
        required=False,
        multiple=False,
    ),
    "image": Prompt(
        text="Docker image used to deploy challenge",
        type=None,
        default=None,
        required=False,
        multiple=False,
    ),
    "type": Prompt(
        text="Type of challenge",
        type=None,
        default="standard",
        required=True,
        multiple=False,
    ),
    "attempts": Prompt(
        text="How many attempts should the player have",
        type=int,
        default=None,
        required=False,
        multiple=False,
    ),
    "flags": Prompt(
        text="Flags that mark the challenge as solved",
        type=None,
        default=None,
        required=False,
        multiple=True,
    ),
    "tags": Prompt(
        text="Tag that denotes a challenge topic",
        type=None,
        default=None,
        required=False,
        multiple=True,
    ),
    "files": Prompt(
        text="Files to be shared with the user",
        type=None,
        default=None,
        required=False,
        multiple=True,
    ),
    "hints": Prompt(
        text="Hints to be shared with the user",
        type=None,
        default=None,
        required=False,
        multiple=True,
    ),
    "requirements": Prompt(
        text="Challenge dependencies that must be solved before this one can be attempted",
        type=None,
        default=None,
        required=False,
        multiple=True,
    ),
}


def blank_challenge_spec():
    pwd = Path(__file__)
    spec = pwd.parent.parent / "spec" / "challenge-example.yml"
    with open(spec) as f:
        blank = yaml.safe_load(f)

    for k in blank:
        if k != "version":
            blank[k] = None

    return blank

