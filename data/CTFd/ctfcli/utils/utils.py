import sys
import json
import yaml
import os
import getpass
import tempfile
import pathlib
import logging
import traceback
import subprocess
from pathlib import Path

from collections import namedtuple
from urllib.parse import urlparse

try:
    #import colorama
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
log_file            = 'logfile'
logging.basicConfig(filename=log_file, 
                    #format='%(asctime)s %(message)s', 
                    filemode='w'
                    )
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

###############################################
# returns subdirectories , without . files/dirs
# name of the yaml file expected to have the challenge data in each subfolder
basechallengeyaml   = "challenge.yml"
def getsubdirs(directory):
    '''
    Returns folders in a directory as Paths
    '''
    wat = []
    for filepath in pathlib.Path(directory).glob('**/*'):#.iterdir():
       if (Path(filepath).is_dir()):
           wat.append(Path(filepath))
    return wat

def getsubfiles(directory):
    '''
    Returns files in a directory as Paths
    '''
    wat = [Path(filepath) for filepath in pathlib.Path(directory).glob('**/*')]
    return wat

# open with read operation
challengeyamlbufferr = lambda category,challenge: open(os.path.join(category,challenge,basechallengeyaml),'r')
# open with write operation
challengeyamlbufferw = lambda category,challenge: open(os.path.join(category,challenge,basechallengeyaml),'r')
#loads a challenge.yaml file into a buffer
loadchallengeyaml =  lambda category,challenge: yaml.load(challengeyamlbufferr(category,challenge), Loader=yaml.FullLoader)
writechallengeyaml =  lambda category,challenge: yaml.load(challengeyamlbufferw(category,challenge), Loader=yaml.FullLoader)
# simulation of a chdir command to "walk" through the repo
# helps metally
#location = lambda currentdirectory,childorsibling: Path(currentdirectory,childorsibling)
# gets path of a file
getpath = lambda directoryitem: Path(os.path.abspath(directoryitem))
################################################################################
##############             ERROR HANDLING FUNCTIONS            #################
################################################################################
def errorlogger(message):
    """
    prints line number and traceback
    TODO: save stack trace to error log
            only print linenumber and function failure
    """
    exc_type, exc_value, exc_tb = sys.exc_info()
    trace = traceback.TracebackException(exc_type, exc_value, exc_tb) 
    errormesg = message + ''.join(trace.format_exception_only())
    #traceback.format_list(trace.extract_tb(trace)[-1:])[-1]
    lineno = 'LINE NUMBER >>>' + str(exc_tb.tb_lineno)
    logger.error(lineno+errormesg)
    print(lineno+errormesg + ''.join(trace.format_exception_only()))

        
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

CATEGORIES = [
    "exploitation",
    "reversing",
    "web",
    "forensics",
    "scripting",
    "crypto",
    "networking",
    "linux",
    "miscellaneous"
    ]

ctfdurl = str
APIPREFIX = "/api/v1/"
CTFd_API_ROUTES = {"challenges": f"{APIPREFIX}challenges",
    "tags":f"{ctfdurl}{APIPREFIX}tags", 
    "topics":f"{ctfdurl}{APIPREFIX}topics", 
    "awards":f"{ctfdurl}{APIPREFIX}awards", 
    "hints":f"{ctfdurl}{APIPREFIX}hints", 
    "flags":f"{ctfdurl}{APIPREFIX}flags", 
    "submissions":f"{ctfdurl}{APIPREFIX}submissions", 
    "scoreboard":f"{ctfdurl}{APIPREFIX}scoreboard", 
    "teams":f"{ctfdurl}{APIPREFIX}teams", 
    "users":f"{ctfdurl}{APIPREFIX}users", 
    "statistics":f"{APIPREFIX}statistics",
    "files":f"{APIPREFIX}files", 
    "notifications":f"{APIPREFIX}notifications", 
    "configs":f"{APIPREFIX}configs", 
    "pages":f"{APIPREFIX}pages", 
    "unlocks":f"{APIPREFIX}unlocks", 
    "tokens":f"{APIPREFIX}tokens", 
    "comments":f"{APIPREFIX}comments"}
