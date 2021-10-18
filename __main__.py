# This file is going to be the main file after start.sh I guess?

# HUGE TODO: SET PATHS CORRECTLY EVERYTHING IS BROKENNNN!!!!!
# repository managment
from ctfcli.__main__ import Ctfcli
from ctfcli.utils.utils import greenprint,errorlogger
# basic imports
import subprocess
import os,sys,fire
from pathlib import Path
from pygments import formatters, highlight, lexers
from pygments.util import ClassNotFound
from simple_term_menu import TerminalMenu


def highlight_file(filepath):
    with open(filepath, "r") as f:
        file_content = f.read()
    try:
        lexer = lexers.get_lexer_for_filename(filepath, stripnl=False, stripall=False)
    except ClassNotFound:
        lexer = lexers.get_lexer_by_name("text", stripnl=False, stripall=False)
    formatter = formatters.TerminalFormatter(bg="dark")  # dark or light
    highlighted_file_content = highlight(file_content, lexer, formatter)
    return highlighted_file_content


def list_files(directory="."):
    return (file for file in os.listdir(directory) if os.path.isfile(os.path.join(directory, file)))


def main():
    terminal_menu = TerminalMenu(list_files(), preview_command=highlight_file, preview_size=0.75)
    menu_entry_index = terminal_menu.show()

################################################################################
##############                   Master Values                 #################
################################################################################

sys.path.insert(0, os.path.abspath('.'))

#Before we load the menu, we need to do some checks
# The .env needs to be reloaded in the case of other alterations
#
# Where the terminal is located when you run the file
PWD = os.path.realpath(".")
#PWD_LIST = os.listdir(PWD)

#where the script itself is located
# ohh look a global
global PROJECT_ROOT
PROJECT_ROOT = Path(os.path.dirname(__file__))
global CHALLENGEREPOROOT
CHALLENGEREPOROOT=Path(PROJECT_ROOT,'/data/CTFd')


###############################################################################

###############################################################################
##                     Docker Information                                    ##
###############################################################################
gitdownloads = {
    "opsxcq":("exploit-CVE-2017-7494","exploit-CVE-2016-10033"),
    "t0kx":("exploit-CVE-2016-9920"),
    "helmL64":"https://get.helm.sh/helm-v3.7.0-linux-amd64.tar.gz",
    "helmW64":"https://get.helm.sh/helm-v3.7.0-windows-amd64.zip"
}
helmchartrepos = {
    "":"helm repo add gitlab https://charts.gitlab.io/",
    "":"helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx",
    "":"helm repo add prometheus-community https://prometheus-community.github.io/helm-charts",
    "":"https://artifacthub.io/packages/helm/slamdev/gitlab-omnibus"
}
helchartinstalls = {
    "":"helm install [RELEASE_NAME] prometheus-community/kube-prometheus-stack"
}
#for pi
raspipulls= {
    "opevpn"    : "cambarts/openvpn",
    "webgoat"   : "cambarts/webgoat-8.0-rpi",
    "bwapp"     : "cambarts/arm-bwapp",
    "dvwa"      : "cambarts/arm-dvwa",
    "LAMPstack" : "cambarts/arm-lamp"
}
#for pi
rpiruns = {
    "bwapp"     : '-d -p 80:80 cambarts/arm-bwapp',
    "dvwa"      : '-d -p 80:80 -p 3306:3306 -e MYSQL_PASS="password" cambarts/dvwa',
    "webgoat"   : "-d -p 80:80 -p cambarts/webgoat-8.0-rpi",
    "nginx"     : "-d nginx",
}


def putenv(key,value):
    """
    Puts an environment variable in place

    For working in the interactive mode when run with 
    >>> hacklab.py -- --interactive
    """
    try:
        os.environ[key] = value
        greenprint(f"[+] {key} Env variable set to {value}")
    except Exception:
        errorlogger(f"[-] Failed to set {key} with {value}")

def setenv(**kwargs):
    '''
    sets the environment variables given by **kwargs

    The double asterisk form of **kwargs is used to pass a keyworded, 
    variable-length argument dictionary to a function. 
    '''
    try:
        if __name__ !="" and len(kwargs) > 0:
            projectname = __name__
            for key,value in kwargs:
                putenv(key,value)

            putenv("COMPOSE_PROJECT_NAME", projectname)
        else:
            raise Exception
    except Exception:
        errorlogger("""[-] Failed to set environment variables!\n
    this is an extremely important step and the program must exit now. \n
    A log has been created with the information from the error shown,  \n
    please provide this information to the github issue tracker""")
        sys.exit(1)


def certbot(siteurl):
    '''
    creates cert with certbot
    '''
    generatecert = 'certbot --standalone -d {}'.format(siteurl)
    subprocess.call(generatecert)

def certbotrenew():
    renewcert = '''certbot renew --pre-hook "docker-compose -f path/to/docker-compose.yml down" --post-hook "docker-compose -f path/to/docker-compose.yml up -d"'''
    subprocess.call(certbotrenew)    
    
#lol so I know to implement it later
#certbot(siteurl)

def createsandbox():
    '''
    Creates a sandbox
    '''

def runsandbox(composefile):
    '''
    run a sandbox

    Args:
        composefile (str): composefile to use
    '''
    subprocess.Popen(["docker-compose", "up", composefile])

################################################################################
##############      The project formerly known as sandboxy     #################
################################################################################
class Project():
    def __init__(self,projectroot:Path):
        self.root = projectroot
        self.datadirectory = Path(self.root, "data")
        self.extras = Path(self.root, "extra")
        self.containerfolder = Path(self.root, "containers")
        self.mysql = Path(self.root, "data", "mysql")
        self.redis = Path(self.root, "data", "redis")
        self.persistantdata = [self.mysql,self.redis]

    #def setkubeconfig(self):
    #    # Configs can be set in Configuration class directly or using helper utility
    #    self.config = config.load_kube_config()
    #    self.client = client.CoreV1Api()

    def cleantempfiles(self):
        """
        Cleans temoporary files
        """
        for directory in self.persistantdata:
            # clean mysql
            for file in os.listdir(directory):
                if os.exists(Path(os.path.abspath(file))):
                    os.remove(Path(os.path.abspath(file)))
            # clean redis
            #for file in os.listdir(self.mysql):
            #    os.remove(Path(os.path.abspath(file)))


                
class MenuGrouping():
    '''
        DO NOT MOVE THIS FILE


    '''
    def __init__(self):
        # challenge templates
        self.name = "lol"
        self.project_actions = Project(PROJECT_ROOT)
        self.cli = Ctfcli()

def main():
   fire.Fire(MenuGrouping)


if __name__ == "__main__":
    main()
    #fire.Fire(Ctfcli)