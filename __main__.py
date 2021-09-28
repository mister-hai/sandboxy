# This file is going to be the main file after start.sh I guess?

# repository managment
from ctfcli.__main__ import Ctfcli

# basic imports
import subprocess
import os,sys,fire,yaml
from pathlib import Path

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
    "t0kx":("exploit-CVE-2016-9920")
}
#for pi
envvars = {
    "WEBGOAT_PORT"      : "18080",
    "WEBGOAT_HSQLPORT"  : "19001",
    "WEBWOLF_PORT"      : "19090",
    "BRIDGE_ADDRESS"    : "172.21.1.1/24"
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
        error("""[-] Failed to set environment variables!\n
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
certbot(siteurl)



def installfromapt(csvconfiglist):
    '''
    installs from apt repo
    '''
    #aptinstalls = """docker,python3,python3-pip,git,tmux,openvpn"""
    command = "sudo apt-get install -y {}".format(' '.join(csvconfiglist.split(",")))
    subprocess.Popen(command,shell=True)

def installfromgit(user,repo):
    '''

    '''

    #repo = git.Repo.clone(url)
    #repo = git.Repo.clone_from(url, name)

    url = "https://github.com/{user)/{repo}.git".format(user=user,repo=repo)
    proc = subprocess.Popen(["git", "clone", "--progress", url],
                            stdout=os.PIPE,
                            stderr=os.STDOUT,
                            shell=True,
                            text=True)
    for line in proc.stdout:
        if line:
            print(line.strip()) 

    
def createvulnhubenvironment():
    '''
    clones from vulhub on github
    '''
    installfromgit("vulhub","vulhub")

def createsandbox():
    '''
    Creates the sandbox
    '''
    # install packages necessary for the environment
    installfromapt(aptinstalls)
    #initiate the docker project build
    subprocess.Popen(["docker-compose", "build"])

def runsandbox():
    '''
    run the sandbox
    '''
    subprocess.Popen(["docker-compose", "up"])

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

    def setkubeconfig(self):
        # Configs can be set in Configuration class directly or using helper utility
        self.config = config.load_kube_config()
        self.client = client.CoreV1Api()

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


                
class Sandboxy():
    '''
        DO NOT MOVE THIS FILE


    '''
    def __init__(self):
        # challenge templates
        self.name = "lol"
        self.project_actions = Project(PROJECT_ROOT)
        self.cli = Ctfcli()

def main():
   fire.Fire(Sandboxy)


if __name__ == "__main__":
    main()
    #fire.Fire(Ctfcli)