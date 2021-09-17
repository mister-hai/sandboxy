import yaml, os
from pathlib import Path
from ctfcli.utils.utils import errorlogger,greenprint
from yaml import safe_load,safe_dump

class Yaml(): #filetype
    """
    Base class for challenges and the repo

    Anything thats a yaml file inherits from this
    Args:
        filepath (str): Full Filepath to Yaml File to load
    """
    def __init__(self, filepath:Path):
        self.filename = os.path.basename(filepath)
        self.filepath = filepath
        self.directory = self.filepath.parent
        if self.filename.endswith(".yaml"):
            greenprint("[!] File is .yaml! Presuming to be kubernetes config!")
            self.type = "kubernetes"
        elif self.filename.endswith(".yml"):
            greenprint("[!] Challenge File presumed (.yml)")
            self.type = "challenge"

    def loadyaml(self, filepath):
        """
        Loads the yaml specified by the class variable Yaml.filepath
        """
        try:
            with open(filepath, 'r') as stream:
                return yaml.safe_load(stream)
        except Exception:
            errorlogger("[-] ERROR: Could not load .yml file")
    
    def writeyaml(self):
        """
        Remember to assign data to the file with

        >>> thing = Yaml(filepath)
        >>> thing.data['key'] = value
        """
        try:
            #open the yml file pointed to by the load operation
            with open(self.filepath) as file:
                safe_dump(file)
        except Exception:
            errorlogger("[-] ERROR: Could not Write .yml file, check the logs!")


class MasterFile(Yaml):
    """
    Protoclass for the masterlist, this helps avoid 
    circular imports and allows you to split code apart more
    """
    def __new__(cls,*args, **kwargs):
        cls.__name__ = 'MasterFile'
        cls.__qualname__= 'MasterFile'
        cls.tag = '!Masterlist'
        return super(cls).__new__(cls, *args, **kwargs)

class KubernetesYaml(Yaml): #file
    """
    Represents a Kubernetes specification
    future
    """
    def __init__(self):
        super().__init__()
