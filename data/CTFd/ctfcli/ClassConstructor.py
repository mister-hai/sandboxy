import yaml,os
from yaml import SafeLoader,SafeDumper,MappingNode
from utils.utils import errorlogger,redprint,yellowboldprint,greenprint,CATEGORIES
from utils.challenge import Challenge
from pathlib import Path
from yaml import SafeLoader,SafeDumper,MappingNode,safe_load,safe_dump
import hashlib


# Tutorial`        
class ClassA():
    def __init__(self, message):
        print(message)

class ClassB():
    """
    An example of how to dynamically create classes based on params

    Args:
        codeobject (object): An arbitrary function or bit of code as a single object
    """
    def __init__(self, codeobject, message:str):
        codeobject(message)

class Proto2():
    """
    The Class used to represent a repository
    """
    def __init__(self,**entries):
        self.__dict__.update(entries)
        self.ClassA(self.message)

# Quick test to check if modifications have affected base function
# testinstance = ClassB(ClassA,message="this message is piped through the scope to an arbitrary class")
#asdf = {"id":1,"name":"testrepository","ClassA": testinstance ,"tag":'!Repo'}
#qwer = Proto2(**asdf)
#qwer

###############################################################################
#  CTFd Repository
# 
###############################################################################

class Repo():
    #def __new__(cls,*args, **kwargs):
    def __new__(cls,**kwargs):
        cls.__name__ = "Repo"
        cls.__qualname__= 'Repo'
        cls.tag = '!Repo'
        return super().__new__(cls)
        #return super(cls).__new__(cls, *args, **kwargs)

class Repository(Repo):
    """
    Representation of a repository as exists in the challenges folder

    Args:
        **kwargs (dict): Feed it a dict of Category()'s with Challenge()'s appended
    """
    def __init__(self,**entries): 
        self.__dict__.update(entries)


class Yaml(): #filetype
    """
    Represents a challange.yml
    Give Path to challenge.yml

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

    def loadyaml(self):
        """
        Loads the yaml specified by the class variable Yaml.filepath
        """
        try:
            with open(self.filepath) as f:
                filedata = safe_load(f.read())#, filepath=filepath)
                self.data = filedata
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
    def __new__(cls,*args, **kwargs):
        cls.__name__ = 'repo'
        cls.__qualname__= 'repo'
        cls.tag = '!Masterlist'
        return super(cls.__name__, cls).__new__(cls, *args, **kwargs)

class KubernetesYaml(Yaml): #file
    """
    Represents a Kubernetes specification
    future
    """
    def __init__(self):
        super().__init__()

class Challengeyaml(Yaml): #file
    """
    Represents the challenge.yml as exists in the folder for that specific challenge

    Until now, it was a seperate class but now we merge the yaml and the program itself
    by supplying a dict 
    >>> filepath = os.path.abspath("challenge.yaml")
    >>> newchallenge = Challengeyaml(filepath)

    """
    def __init__(self,yamlfile):
        #get a representation of the challenge.yaml file
        yamlcontents = self.loadyaml(yamlfile)
        self.loadchallengeyaml(**yamlcontents)

        # internal data
        self.id = str
        self.synched = bool
        self.installed = bool
        super().__init__()

    def loadchallengeyaml(self,**entries):
        """
        Unpacks a dict representation of the challenge.yaml into
        The Challengeyaml() Class, this is ONLY for challenge.yaml

        The structure is simple and only has two levels, and no stored code

        >>> asdf = Challengeyaml(filepath)
        >>> print(asdf.category)
        >>> 'Forensics'

        The new challenge name is created by:

        >>> self.__name = "Challenge_" + str(hashlib.sha256(self.name))
        >>> self.__qualname__ = "Challenge_" + str(hashlib.sha256(self.name))
        
        Resulting in a name similar to 
        Args:
            yamlfile (str): Full Path to the challenge.yaml
            **entries (dict): Dict returned from a yaml.load() operation
        """
        # unpack supplied dict
        self.__dict__.update(entries)
        # the new classname is defined by the name tag in the Yaml now
        self.__name = "Challenge_" + str(hashlib.sha256(self.name))
        self.__qualname__ = "Challenge_" + str(hashlib.sha256(self.name))
class Masterlist(MasterFile):
    """
    This is one way of turning a yaml into a class

    https://matthewpburruss.com/post/yaml/

    """
    def __init__(self, masterlistfile =  "masterlist.yml"):
        # filename for the full challenge index
        self.masterlistfile      = masterlistfile
        self.masterlistlocation  = os.path.join(self.challengesfolder, self.masterlistfile)
        #self.masterlist          = Yaml(self.masterlistlocation)
        # tag for yaml file
        self.tag = "!Masterlist:"
        self.repotag = "!Repo:"
        self.categorytag = "!Category:"
        self.challengetag = "!Challenge:"
        super().__init__()

    def _representer(self, tag, dumper: SafeDumper, codeobject) -> MappingNode:
        """
        Represent a Object instance as a YAML mapping node.

        This is part of the Output Flow from Python3.9 -> Yaml

        In the Representer Class/Function You must define a mapping
        for the code to be created from the yaml markup

        Args:
            tag (str) : tag to assign object in yaml file
            codeobject (str): python code in a single object
        """
        return dumper.represent_mapping(tag, codeobject)
 
    def _multiconstructor(self, loader: SafeLoader, node: yaml.nodes.MappingNode, type="masterlist"):
        """
        Construct an object based on yaml node input

        Args:
            type (str): 'masterlist' || 'repo' || 'challenge'
        """
        
        if type == "masterlist":
            return Masterlist(**loader.construct_mapping(node, deep=True))
        elif type == 'repo':
            return Repository(**loader.construct_mapping(node, deep=True))
        elif type== "challenge":
            return Challenge(**loader.construct_mapping(node, deep=True))

    def _get_dumper(self,tag:str, constructor, classtobuild):
        """
        Add representers to a YAML serializer.

        Converts Python to Yaml
        """
        safe_dumper = SafeDumper
        safe_dumper.add_representer(classtobuild, self._representer)
        return safe_dumper
 
    def _get_loader(self, constructor):#,tag:str):
        """
        Add constructors to PyYAML loader.

        Converts Yaml to Python
        Args:
            tags (str): the tag to use to mark the yaml object in the file
            constructor (function): the constructor function to call
        """
        loader = SafeLoader
        #loader.add_constructor(tag, constructor)
        loader.add_multi_constructor(self.tag, self.multi_constructor_masterlist)
        loader.add_multi_constructor(self.repotag, self.multi_constructor_repo)
        loader.add_multi_constructor(self.categorytag, self.multi_constructor_category)
        loader.add_multi_constructor(self.challengetag, self.multi_constructor_obj)

        return loader
    
    def _loadmasterlist(self):
        """
        Loads the masterlist.yaml into Masterlist.data

        Args:
            masterlistfile (str): The file to load as masterlist, defaults to masterlist.yamlw
        """
        try:
            #open the yml
            # feed the tag and the constructor method to call
            return yaml.load(open(self.masterlistlocation, 'rb'), 
                Loader=self._get_loader(self.tag,self._constructor))
        except Exception:
            errorlogger("[-] ERROR: Could not load .yml file")

    def _writenewmasterlist(self, pythoncode, filemode="a"):
        """
        Creates a New Masterlist.yaml file from an init command
        remember to assign data to the file with
        
        >>> thing = Masterlist(filepath)
        >>> thing.data = Category()
        >>> thing.writeyaml()

        Args: 
            pythoncode (Object): an instance of a python object to transform to YAML
            filemode (str) : File Mode To open File with. set to append by default
                             so you can manually fix the repo list

        """
        try:
            with open("output.yml", filemode) as stream:
                yellowboldprint("[+] Attempting To Write Masterlist.yaml")
                stream.write(yaml.dump(pythoncode,
                        Dumper=self._get_dumper(self.tag,self._multiconstructor())))
                greenprint("[+] Masterlist.yaml written to disk!")
        except Exception:
            errorlogger("[-] ERROR: Could not Write .yml file, check the logs!")

    def _loadmasterlist(self, loadedyaml:dict)-> Repo:
        """
        Transforms Yaml data to Python objects for loading and unloading
        """
        try:
            return yaml.load(open(self.masterlistlocation, 'rb'),
                        Loader=self._get_loader("!Masterlist"))
        except Exception:
            errorlogger("[-] ERROR: Could not load .yml file")

    def _writemasteryaml(self,name:str, filemode="a"):
        """

        """
        try:
            #open the yml file pointed to by the load operation
            with open(self.filepath, filemode) as file:
                #file.write()
                yaml.dump(file)
        except Exception:
            errorlogger("[-] ERROR: Could not Write .yml file, check the logs!")


###############################################################################
#  CTFd CATEGORY: representation of folder in repository
###############################################################################
class Category(): #folder
    """
    use getattr(),setattr() to add/query Challenge Entries
    this is used for keeping track internally

    ChallengeCategory:
        represents a folder in the PROJECTDIRECTORY/data/CTFd/challenges/ dir
      ChallengeEntry:
        represents a challenge.yaml
        name: thing
    """
    def __init__(self,category,location):
        self.name = category
        self.location = location
    
    def _addchallenge(self, challenge:Challenge):
        """
        Adds a challenge to the repository, appended to Category() class

        Args:
            challenge (Challenge): Challenge() object from folder in repository
        """
        if challenge.category in CATEGORIES:
            setattr(challenge.category,challenge.name,challenge)
        else:
            errorlogger(f"[-] Category.addchallenge failed with {challenge.category}")
            raise ValueError

class Challenge():
    def __new__(cls,**kwargs):
        cls.__name__ = ''
        cls.__qualname__= ''
        cls.tag = '!Challenge'
        return super().__new__(cls)

    def __init__(self):
        """
        Base Class for all the attributes required on both the CTFd side and Repository side

        Args:
            **kwargs (dict): Dict from Yaml.loadchallengeyaml(filepath)
        """

###############################################################################
#  Handout folder
###############################################################################
class Handout():
    """
    Represents a Handout folder for files and data to be given to the
    CTF player
    """
    def __init__(self):
        pass
###############################################################################
#  Solution folder
###############################################################################
class Solution():
    """
    Represents a Solution folder for data describing the methods and 
    steps necessary to solve the challenge and capture the flag
    """
    def __init__(self):
        pass