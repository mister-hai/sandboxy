# This file is going to be the main file after start.sh I guess?

# repository managment
from ctfcli.__main__ import Ctfcli

# deployment managment
from kubernetes import client, config, watch
import docker

# basic imports
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

    def listallpods(self):
        self.setkubeconfig()
        # Configs can be set in Configuration class directly or using helper utility
        print("Listing pods with their IPs:")
        ret = self.client.list_pod_for_all_namespaces(watch=False)
        for i in ret.items:
            print("%s\t%s\t%s" % (i.status.pod_ip, i.metadata.namespace, i.metadata.name))

    def watchpodevents(self):
        self.setkubeconfig()
        count = 10
        watcher = watch.Watch()
        for event in watcher.stream(self.client.list_namespace, _request_timeout=60):
            print("Event: %s %s" % (event['type'], event['object'].metadata.name))
            count -= 1
            if not count:
                watcher.stop()
                
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