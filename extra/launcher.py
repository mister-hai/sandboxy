#!/usr/bin/python3
# https://github.com/vulhub/vulhub.git
# https://github.com/giper45/DockerSecurityPlayground
# https://cheatsheetseries.owasp.org/cheatsheets/Docker_Security_Cheat_Sheet.html
# https://github.com/aaaguirrep/offensive-docker
# https://github.com/agrawalsmart7/docker-pentesting
# https://hub.docker.com/u/vulnerables
# https://github.com/vulhub/vulhub
# https://hub.docker.com/r/vulnerables/web-dvwa
################################################################################
##############                      IMPORTS                    #################
################################################################################
import git
import yaml
import docker
import sys,os
import zipfile
import pathlib
import argparse
import subprocess
import configparser
from git import Repo
from extra.shellops import *

__name__ = "SANDBOXENV"

################################################################################
##############             COMMAND LINE ARGUMENTS              #################
################################################################################

PROGRAM_DESCRIPTION = """Ctf Environment Setup for raspi4b, 
You run this once, in a new environment, I.E a VM, and it sets up an environment"""
# that can also be used for ctf sandboxing

parser = argparse.ArgumentParser(description=PROGRAM_DESCRIPTION)
parser.add_argument('--configfile',
                        dest = 'configfile',
                        action  = "store",
                        default = "conf.conf" ,
                        help = " use this flag for changing the config file",
                        required=False
                        )
parser.add_argument('--configset',
                        dest = 'configset',
                        action  = "store",
                        default = "DEFAULT" ,
                        help = " use this flag to select which configuration to use",
                        required=False
                        )
parser.add_argument('--rpi',
                        dest = 'rpi',
                        action  = "store_true",
                        default = False ,
                        help = " use this flag if you are running this script on a raspberry pi",
                        required=False
                        )
try:
    #parse args to get defaults
    arguments = parser.parse_args()
except Exception:
    print("[-] Args could not be parsed!")
    sys.exit(1)

greenprint("[+] Loaded Commandline Arguments")

def error(message):
    '''
    prints line number and traceback
    TODO: save stack trace to error log
            only print linenumber and function failure
    '''
    exc_type, exc_value, exc_tb = sys.exc_info()
    trace = traceback.TracebackException(exc_type, exc_value, exc_tb) 
    errormesg = message + ''.join(trace.format_exception_only())
    #traceback.format_list(trace.extract_tb(trace)[-1:])[-1]
    lineno = 'LINE NUMBER >>>' + str(exc_tb.tb_lineno)
    print(lineno)
    print(errormesg)

###############################################################################
##                     Docker Information                                    ##
###############################################################################
#connects script to docker on host machine
client = docker.from_env()
runcontainerdetached = lambda container: client.containers.run(container, detach=True)
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

def startcontainerset(containerset:dict):
    ''' 
    Starts the set given by params
    '''
    for name,container in containerset.items:
        runcontainerdetached(container=containerset[name])

def runcontainerwithargs(container:str,arglist:list):
    client.containers.run(container, arglist)

def listcontainers():
    '''
    lists installed containers
    '''
    for container in client.containers.list():
        print(container.name)


def opencomposefile(docker_config):
    '''
    '''
    with open(docker_config, 'r') as ymlfile:
        docker_config = yaml.load(ymlfile)

def writecomposefile(docker_config,newyamldata):
    with open(docker_config, 'w') as newconf:
        yaml.dump(docker_config, newyamldata, default_flow_style=False)

#with zipfile.ZipFile(terraformamd64zip,"r") as zip_ref:
#   terraformbinary = zip_ref.extractall("targetdir")

def putenv(var,val):
    '''
    pushes an item into an ENV var
    '''
    os.environ[var] = val 

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
    A log has been created with the imformation from the error shown,  \n
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

if __name__ == "__main__":
    createsandbox()