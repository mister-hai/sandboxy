# this file gets moved to the following location
# /sandboxy/ctfcli/core/dockerrepo.py

# deployment managment
from kubernetes import client, config, watch
import docker,yaml

class DockerManagment():
    def __init__(self):
        #connects script to docker on host machine
        client = docker.from_env()
        self.runcontainerdetached = lambda container: client.containers.run(container, detach=True)

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

    def startcontainerset(self,containerset:dict):
        ''' 
        Starts the set given by params
        '''
        for name,container in containerset.items:
            self.runcontainerdetached(container=containerset[name])

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
