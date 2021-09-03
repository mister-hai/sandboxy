from pathlib import Path
import os
import yaml
from yaml import SafeLoader,SafeDumper,MappingNode,safe_load,safe_dump
from utils.utils import greenprint, redprint, errorlogger
#https://matthewpburruss.com/post/yaml/
# This is one way of turning a yaml into a class

class Repo():
    def __new__(cls,*args, **kwargs):
        cls.__name__ = 'Repo'
        cls.__qualname__= 'Repo'
        cls.tag = '!Repo'
        return super(cls.__name__, cls).__new__(cls, *args, **kwargs)

class Repository(Repo):
    def __init__(self,**entries): 
        self.__dict__.update(entries)

    def repo_representer(self, tag, dumper: SafeDumper, code) -> MappingNode:
        """
        Represent a Masterlist instance as a YAML mapping node.
        """
        return dumper.represent_mapping(tag, code)
 
    def repo_constructor(self, loader: SafeLoader, node: MappingNode):
        """
        Construct A Repo object from the Yaml file contents
        """
        return Repo(**loader.construct_mapping(node))

    def get_dumper(self,tag:str, constructor):
        """
        Add representers to a YAML serializer.
        """
        safe_dumper = SafeDumper
        safe_dumper.add_representer(Masterlist, self.repo_representer)
        return safe_dumper
 
    def get_loader(self,tag:str, constructor):
        """
        Add constructors to PyYAML loader.

        Args:
            tags (str): the tag to use to mark the yaml object in the file
            constructor (function): theconstructor function to call
        """
        loader = SafeLoader
        loader.add_constructor(tag, constructor)
        return loader


    def construct(self, loader: SafeLoader, node: MappingNode) -> Repo:
        '''
        Builder for Repo Objects
        '''
        return Repo(**loader.construct_mapping(node))

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

class Masterlist(MasterFile):
    def __init__(self, masterlistfile =  "masterlist.yml"):
        # filename for the full challenge index
        self.masterlistfile      = masterlistfile
        self.masterlistlocation  = os.path.join(self.challengesfolder, self.masterlistfile)
        #self.masterlist          = Yaml(self.masterlistlocation)
        # tag for yaml file
        self.tag = "!Masterlist"
        super().__init__()

    def _representer(self, tag, dumper: SafeDumper, codeobject) -> MappingNode:
        """
        Represent a Masterlist instance as a YAML mapping node.

        Args:
            tag (str) : tag to assign object in yaml file
            codeobject (str): python code in a single object
        """
        return dumper.represent_mapping(tag, codeobject)
 
    def _constructor(self, loader: SafeLoader, node: MappingNode, codeobject:object):
        """
        Construct A object from the Yaml file
        """
        return codeobject(**loader.construct_mapping(node))

    def _get_dumper(self,tag:str, constructor, classtobuild):
        """
        Add representers to a YAML serializer.
        """
        safe_dumper = SafeDumper
        safe_dumper.add_representer(classtobuild, self._masterlist_representer)
        return safe_dumper
 
    def _get_loader(self,tag:str, constructor):
        """
        Add constructors to PyYAML loader.

        Args:
            tags (str): the tag to use to mark the yaml object in the file
            constructor (function): theconstructor function to call
        """
        loader = SafeLoader
        loader.add_constructor(tag, constructor)
        return loader
    
    def _loadmasterlist(self):
        """
        Loads the masterlist.yaml into Masterlist.data

        Args:
            masterlistfile (str): The file to load as masterlist, defaults to masterlist.yamlw
        """
        # loads the data
        try:
            #open the yml
            # feed the tag and the constructor method to call
            #self.data = 
            return yaml.load(open(self.masterlistlocation, 'rb'), Loader=self._get_loader(self.tag,self._constructor))
        except Exception:
            errorlogger("[-] ERROR: Could not load .yml file")

    def _writenewmasterlist(self, pythoncode):
        '''
        Creates a New Masterlist.yaml file from an init command
        '''
        with open("output.yml", "w") as stream:
            stream.write(yaml.dump(pythoncode, Dumper=self._get_dumper(self.tag,self._constructor())))
    
    def _transformyamltorepository(self, loadedyaml:dict)-> Repo:
        '''
        Transforms Yaml data to Python objects for loading and unloading
        '''
        try:
            #open the yml
            # feed the tag and the constructor method to call
            #self.data = 
            return yaml.load(open(self.masterlistlocation, 'rb'), Loader=self._get_loader("!Repo",Repo.construct()))
        except Exception:
            errorlogger("[-] ERROR: Could not load .yml file")
        #defaults to name "Repo"
        #pythonobjects = Repo(**loadedyaml)
        #return pythonobjects

    def _writemasteryaml(self,name:str, filemode="a"):
        '''
        Special function to write the master yaml for the ctfd side of the repository
        remember to assign data to the file with
        
        >>> thing = Masterlist(filepath)
        >>> thing.data = Category()
        >>> thing.writeyaml()

        File mode is set to append by default so you can manually fix the repo list

        '''
        try:
            #open the yml file pointed to by the load operation
            with open(self.filepath, filemode) as file:
                #file.write()
                yaml.dump(file)
        except Exception:
            errorlogger("[-] ERROR: Could not Write .yml file, check the logs!")

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


