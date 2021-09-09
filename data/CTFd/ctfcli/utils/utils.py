import sys
import json
import yaml
import os,re
import getpass
import tempfile
import pathlib
import logging
import traceback
import subprocess
from pathlib import Path

from collections import namedtuple
from urllib.parse import urlparse
from pygments import highlight
from pygments.formatters import TerminalFormatter
from pygments.lexers import IniLexer, JsonLexer
import configparser

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

###############################################
# returns subdirectories , without . files/dirs
# name of the yaml file expected to have the challenge data in each subfolder
basechallengeyaml   = "challenge.yml"
def getsubdirs(directory):
    '''
    Returns folders in a directory as Paths
    '''
    wat = []
    for item in os.listdir(os.path.normpath(directory)):
       if (not os.path.isfile(os.path.join(directory, item))) and not re.match(r'\..*', item):
           wat.append(item)
    return wat

def getsubfiles(directory):
    '''
    Returns files in a directory as Paths
    '''
    wat = []
    for item in os.listdir(os.path.normpath(directory)):
       if (os.path.isfile(os.path.join(directory, item))) and not re.match(r'\..*', item):
           wat.append(item)
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

APIPREFIX = "/api/v1/"
CTFd_API_ROUTES = {"challenges": f"{APIPREFIX}challenges",
              "tags":f"{APIPREFIX}tags", 
              "topics":f"{APIPREFIX}topics", 
              "awards":f"{APIPREFIX}awards", 
              "hints":f"{APIPREFIX}hints", 
              "flags":f"{APIPREFIX}flags", 
              "submissions":f"{APIPREFIX}submissions", 
              "scoreboard":f"{APIPREFIX}scoreboard", 
              "teams":f"{APIPREFIX}teams", 
              "users":f"{APIPREFIX}users", 
              "statistics":f"{APIPREFIX}statistics",
              "files":f"{APIPREFIX}files", 
              "notifications":f"{APIPREFIX}notifications", 
              "configs":f"{APIPREFIX}configs", 
              "pages":f"{APIPREFIX}pages", 
              "unlocks":f"{APIPREFIX}unlocks", 
              "tokens":f"{APIPREFIX}tokens", 
              "comments":f"{APIPREFIX}comments"}
              

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


class Config():
    '''
Config class
Maps to the command
host@server$> ctfcli config <command>
    '''
    def __init__(self, configpath):
        self.configpath = configpath
        parser = configparser.ConfigParser()
        # Preserve case in configparser
        parser.optionxform = str
        parser.read(Path(self.configpath))
        return parser

    def edit(self, editor="micro"):
        '''
        ctfcli config edit
            Edit config with $EDITOR
        '''
        # set environment variables for editor
        editor = os.getenv("EDITOR", editor)
        command = editor, 
        subprocess.call(command)

    def path(self):
        '''
        ctfcli config path
            Show config path
        '''
        print("[+] Config located at {}".format(self.configpath))
    
    def loadalternativeconfig(self, configpath:str):
        '''
        Loads an alternative configuration
        ctfcli config loadalternativeconfig <configpath>
        '''
        #path = self.configpath
        parser = configparser.ConfigParser()
        # Preserve case in configparser
        parser.optionxform = str
        parser.read(Path(configpath))
        return parser

    def previewconfig(self, as_string=False):
        '''
        Shows current configuration
        ctfcli config previewconfig
        '''
        config = self.load_config(self.configpath)
        d = {}
        for section in config.sections():
            d[section] = {}
            for k, v in config.items(section):
                d[section][k] = v
        preview = json.dumps(d, sort_keys=True, indent=4)
        if as_string is True:
            return preview
        else:
            print(preview)
    
    def view(self, color=True, json=False):
        
        '''
        view the config
        ctfcli config view
        '''
        with open(self.configlocation) as f:
            if json is True:
                config = self.preview_config(as_string=True)
                if color:
                    config = highlight(config, JsonLexer(), TerminalFormatter())
            else:
                config = f.read()
                if color:
                    config = highlight(config, IniLexer(), TerminalFormatter())
            print(config)
