from pathlib import Path
import os
import yaml
from yaml import SafeLoader,SafeDumper,MappingNode,safe_load,safe_dump
from utils.utils import greenprint, redprint, errorlogger


class Yaml(): #filetype
    '''
    Represents a challange.yml
    Give Path to challenge.yml
    '''
    def __init__(self, filepath:Path):
        # kubernetes or ctfd
        self.type = str
        # sets name of Yaml() to name of file
        self.filename = os.path.basename(filepath)
        self.filepath = filepath
        self.directory = self.filepath.parent
        #if its a kubernetes config
        if self.filename.endswith(".yaml"):
            greenprint("[!] File is .yaml! Presuming to be kubernetes config!")
            self.type = "kubernetes"
        elif self.filename.endswith(".yml"):
            greenprint("[!] Challenge File presumed (.yml)")
            self.type = "challenge"
        # finally, load the file
        #self.loadyaml(filepath)

    def loadyaml(self):
        try:
            #open the yml file
            with open(self.filepath) as f:
                filedata = safe_load(f.read())#, filepath=filepath)
                self.data = filedata
        except Exception:
            errorlogger("[-] ERROR: Could not load .yml file")
    
    def writeyaml(self):
        '''
        remember to assign data to the file with
        >>> thing = Yaml(filepath)
        >>> thing.data['key'] = value
        
        OR... you can assign python objects and store the contents of whole classes
        
        >>> thing.data = Category()
        >>> thing.writeyaml()
        '''
        try:
            #open the yml file pointed to by the load operation
            with open(self.filepath) as file:
                safe_dump(file)
        except Exception:
            errorlogger("[-] ERROR: Could not Write .yml file, check the logs!")


class MasterFile(Yaml):
    def __new__(cls,*args, **kwargs):
        cls.__name__ = 'repo'
        cls.__qualname__= 'repo'
        cls.tag = '!Masterlist'
        return super(cls.__name__, cls).__new__(cls, *args, **kwargs)

class KubernetesYaml(Yaml): #file
    '''
    Represents a Kubernetes specification
    future
    '''
    def __init__(self):
        super().__init__()

class Challengeyaml(Yaml): #file
    '''
    Represents the challenge.yml as exists in the folder for that specific challenge
    '''
    def __init__(self,yamlfile):
        #get a representation of the challenge.yaml file
        self.loadyaml(yamlfile)

        # internal data
        self.id
        self.synched = bool
        self.installed = bool
        super().__init__()


