from ctfcli.utils.utils import errorlogger,greenprint,redprint,yellowboldprint
from ctfcli.core.yamlstuff import Yaml,KubernetesYaml
# deployment managment
from kubernetes import client, config, watch
import docker,yaml

class Deployment():
    """
    Base Class for all the attributes required on both the CTFd side and Repository side
    Represents the challenge.yml as exists in the folder for that specific challenge

    Represents a Challenge Folder
    
    Contents of a Challenge Folder:
        handouts: File or Folder
        solution: File or Folder
        challenge.yaml

    Args:
        yamlfile        (Path): filepath of challenge.yaml
        category        (str):  category to assign to, currently set as folder name
                                needs to be set by yaml tag
        handout         (Path)
        solution        (Path)
    """
    def __init__(self,
            category,
            handout,
            solution,
            readme
            ):
        self.tag = "!Challenge:"
        self.readme = readme
        self.category = category
        #self.deployment         = deployment
        self.solution = solution
        self.handout  = handout

        # this is set after syncing by the ctfd server, it increments by one per
        # challenge upload so it's predictable
        self.id = int

    def _initchallenge(self,**kwargs):
        """
        Unpacks a dict representation of the challenge.yaml into
        The Challenge() Class, this is ONLY for challenge.yaml

        The structure is simple and only has two levels, and no stored code

        >>> asdf = Challenge(filepath)
        >>> print(asdf.category)
        >>> 'Forensics'

        The new challenge name is created by:

        >>> self.__name = "Challenge_" + str(hashlib.sha256(self.name))
        >>> self.__qualname__ = "Challenge_" + str(hashlib.sha256(self.name))
        
        Resulting in a name similar to 
        Args:
            **entries (dict): Dict returned from a yaml.load() operation on challenge.yaml
        """
        # internal data
        self.id = str
        self.synched = bool
        self.installed = bool

        self.jsonpayload = {}
        self.scorepayload = {}
        # we have everything preprocessed
        for each in kwargs:
            setattr(self,each,kwargs.get(each))
        # the new classname is defined by the name tag in the Yaml now
        self.internalname = "Challenge_" + str(sha1(self.name.encode("ascii")).hexdigest())
        self.__name = self.internalname
        self.__qualname__ = self.internalname
        yellowboldprint(f'[+] Internal name: {self.internalname}')


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
