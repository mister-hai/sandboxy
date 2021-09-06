from __future__ import annotations
import hashlib
import yaml,os
from pathlib import Path
from yaml import SafeLoader,SafeDumper,MappingNode
from ctfcli.utils.utils import errorlogger,redprint,yellowboldprint,greenprint,CATEGORIES
from yaml import SafeLoader,SafeDumper,MappingNode,safe_load,safe_dump
from ctfcli.utils.apisession import APISession,APIHandler

# Tutorial
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
        self.codeobject = codeobject
        self.codeobject(message)

class Proto2():
    """
    The Class Accepts a dict of {Classname:Class(params)}
    The Class calls ClassB(ClassA, Message) -> ClassA(message)
    """
    def __init__(self,**entries):
        self.__dict__.update(entries)
        self.ClassA(self.message)

# Quick test to check if modifications have affected base function
# testinstance = ClassB(ClassA,message="this message is piped through the scope to an arbitrary class")
#protopayload = {"ClassA": testinstance}
#qwer = Proto2(**protopayload)
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

    >>> ctfcli ctfdops repo reversing Challenge_SHA256HASHSTRING
    >>> 'Category: Reversing, Challenge Name: "ROPSrFUN4A11"'

    Repository -> Reversing -> Challenge_SHA256HASHSTRING
                            -> Challenge_SHA256HASHSTRING
                            -> Challenge_SHA256HASHSTRING
                            -> Challenge_SHA256HASHSTRING
               -> Forensics 
                            -> Challenge_SHA256HASHSTRING
                            -> Challenge_SHA256HASHSTRING
                            -> Challenge_SHA256HASHSTRING
               -> Web 
                            -> Challenge_SHA256HASHSTRING
                            -> Challenge_SHA256HASHSTRING
                    
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

###############################################################################
#  MASTERLIST
###############################################################################
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
            return Challengeyaml(**loader.construct_mapping(node, deep=True))

    def _get_dumper(self,tag:str, constructor, classtobuild):
        """
        Add representers to a YAML serializer.

        Converts Python to Yaml
        """
        safe_dumper = SafeDumper
        safe_dumper.add_representer(classtobuild, self._representer)
        return safe_dumper
 
    def _get_loader(self, tag:str, constructor):
        """
        Add constructors to PyYAML loader.

        Converts Yaml to Python
        Args:
            tags (str): the tag to use to mark the yaml object in the file
            constructor (function): the constructor function to call
        """
        loader = SafeLoader
        #loader.add_constructor(tag, constructor)
        loader.add_constructor(self.tag, self.multi_constructor_masterlist)
        #loader.add_multi_constructor(self.repotag, self.multi_constructor_repo)
        #loader.add_multi_constructor(self.categorytag, self.multi_constructor_category)
        #loader.add_multi_constructor(self.challengetag, self.multi_constructor_obj)

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
                Loader=self._get_loader(self.tag,self._multiconstructor))
        except Exception:
            errorlogger("[-] ERROR: Could not load .yml file")

    def _writenewmasterlist(self, pythoncode, filemode="a"):
        """
        Creates a New Masterlist.yaml file from an init command
        remember to assign data to the file with
        
        >>> thing = Masterlist(filepath)
        >>> thing._writenewmasterlist(pythoncodeobject)

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

    def _loadmasterlist(self, loadedyaml:dict):
        """
        Transforms Yaml data to Python objects for loading and unloading
        """
        try:
            return yaml.load(open(self.masterlistlocation, 'rb'),
                        Loader=self._get_loader("!Masterlist"))
        except Exception:
            errorlogger("[-] ERROR: Could not load .yml file")

    def writemasteryaml(self,name:str, filemode="a"):
        """
        Writes to an existing master yaml file
        """
        try:
            #open the yml file pointed to by the load operation
            with open(self.filepath, filemode) as file:
                #file.write()
                yaml.dump(file)
        except Exception:
            errorlogger("[-] ERROR: Could not Write .yml file, check the logs!")


###############################################################################
#  CHALLENGEYAML
###############################################################################
class Challengeyaml(Yaml):
    """
    Base Class for all the attributes required on both the CTFd side and Repository side
    Represents the challenge.yml as exists in the folder for that specific challenge

    Represents a Challenge Folder
        If the folder contents are not to specification
        The program will throw an error and refuse to process that folder
    
    Contents of a Challenge Folder:
        handouts: File or Folder
        solution: File or Folder
        challenge.yaml
    
    >>> filepath = os.path.abspath("challenge.yaml")
    >>> newchallenge = Challengeyaml(filepath)

    This Class is where the data from the challenge.yaml ends up
    For modifications to CTFd itself; Additional fields use these
    for arguments in the challenge.yaml
    Optional:
    >>> kwargs.get() 
    Required Arguments:
    >>> kwargs.pop()


    Args:
        yamlfile        (Path): filepath of challenge.yaml
        handout         (Path)
        solution        (Path)
    """
    #def __new__(cls,*args, **kwargs):

#    def __new__(cls,**kwargs):
#        #return super(cls).__new__(cls, *args, **kwargs)
#        return super().__new__(cls)
    
    def __init__(self,
            challengeyaml,
            handout,
            solution
            ):
        self.folderlocation  = Path(os.path.abspath(challengeyaml))
        self.challengefile = challengeyaml
        self.solutiondir = solution
        self.handout = handout

        #get a representation of the challenge.yaml file
        yamlcontents = self.loadyaml(self.challengefile)
        #load the challenge yaml dict into the class
        self._initchallenge(**yamlcontents)
        # unpack supplied dict
        #self.__dict__.update(entries)
        # the new classname is defined by the name tag in the Yaml now
        self.__name = "Challenge_" + str(hashlib.sha256(self.name.encode("ascii")))
        self.__qualname__ = "Challenge_" + str(hashlib.sha256(self.name.encode("ascii")))
        #self.challengesrc       = challengesrc
        #self.deployment         = deployment

    def _initchallenge(self,**kwargs) -> Challengeyaml:
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
            **entries (dict): Dict returned from a yaml.load() operation on challenge.yaml
        """
        # internal data
        self.id = str
        self.synched = bool
        self.installed = bool

        self.jsonpayload = {}
        #Required sections get the "pop()" function 
        # a KeyError will be raised if the key does not exist
        try:
            # Required sections
            category= kwargs.pop("category")
            if category not in CATEGORIES:
                errorlogger("[-] Inconsistancy in challenge.yml, \
                This field should be a Category in approved list {}".format(category))
            else:
                self.category = category
            # set class name as challenge name sha256 hashed
            self.name = kwargs.pop("name")
            self.internalname = "challenge_" + str(hashlib.sha256(self.name.encode("ascii")).hexdigest())
            self.__name__ = "Challenge"
            self.__qualname__= "Challenge"
            self.tag = '!Challenge'

            self.author = kwargs.pop('author')
            self.description = kwargs.pop('description')
            # check for int in challenge value
            if type(kwargs.get('value')) != int:
                raise TypeError
            else:
                self.value = kwargs.pop('value')
            self.type = kwargs.pop('type')
            #path to challenge folder
            self.location = kwargs.pop("location")
            # path to challenge.yml file
            self.challengefile = kwargs.pop("challengefile")
            # Solutions Folder
            self.solutiondir = kwargs.pop("solutiondir")
            # Handout Folder
            self.handout = kwargs.pop("handout")
        except Exception:
            errorlogger("[-] Challenge.yaml does not conform to specification, \
                rejecting. Please check the error log.")
        #self.challengesrc = kwargs.get('challengesrc')
        #self.deployment   = kwargs.get('deployment')
        self.description = kwargs.get('description')
        self.value = kwargs.get('value')
        # can be from masterfile or server, not challenge.yaml
        self.solves = kwargs.get('solves')
        self.solved_by_me = "false"
        # Topics are used to help tell what techniques/information a challenge involves
        # They are generally only visible to admins
        # Accepts strings
        #topics:
        #    - information disclosure
        #    - buffer overflow
        #    - memory forensics
        self.topics = kwargs.get("topics")
        # Tags are used to provide additional public tagging to a challenge
        # Can be removed if unused
        # Accepts strings
        #tags:
        #    - web
        #    - sandbox
        #    - js
        self.tags = kwargs.get("tags")
        #self.template = str
        self.script =  str
        # Hints are used to give players a way to buy or have suggestions. They are not
        # required but can be nice.
        # Can be removed if unused
        # Accepts dictionaries or strings
        self.hints = kwargs.get("hints")
        #    - {
        #        content: "This hint costs points",
        #        cost: 10
        #    }
        #    - This hint is free
        # Requirements are used to make a challenge require another challenge to be
        # solved before being available.
        # Can be removed if unused
        # Accepts challenge names as strings or challenge IDs as integers
        self.requirements = kwargs.get("requirements")
        #    - "Warmup"
        #    - "Are you alive"
        # The state of the challenge.
        # If the field is omitted, the challenge is visible by default.
        # If provided, the field can take one of two values: hidden, visible.
        self.state = kwargs.get("state")
        #state: hidden
        
        # Specifies what version of the challenge specification was used.
        # Subject to change until ctfcli v1.0.0
        #version: "0.1"
        self.version = kwargs.get("version")
        # The extra field provides additional fields for data during the install/sync commands/
        # Fields in extra can be used to supply additional information for other challenge types
        # For example the follow extra field is for dynamic challenges. To use these following
        # extra fields, set the type to "dynamic" and uncomment the "extra" section below
        # extra:
        #     initial: 500
        #     decay: 100
        #     minimum: 50
        self.dynamic = kwargs.get("dynamic")
        # OLD COMMENT
        # Some challenge types (e.g. dynamic) override value.
        # We can't send it to CTFd because we don't know the current value
        if self.dynamic == True:
            extra = kwargs.pop("extra")
            self.scorepayload = {
                        'extra': {
                            'initial': extra['initial'],
                            'decay'  : extra['decay'],
                            'minimum': extra['minimun']
                            }
                        }
        elif self.dynamic == False:
            self.scorepayload = {'value':self.value}
            self.jsonpayload = {
                "name":         self.name,
                "category":     self.category,
                "description":  self.description,
                "type":         self.type,
                **self.scorepayload,
                "author" :      self.author
                }

        #all OPTIONAL values get the GET statement
        # kwargs.get() does not raise an exception when the key does not exist
        # Can be removed if unused
        self.attempts = int
        # Settings used for Dockerfile deployment
        # If not used, remove or set to null
        # If you have a Dockerfile set to .
        # If you have an imaged hosted on Docker set to the image url (e.g. python/3.8:latest, registry.gitlab.com/python/3.8:latest)
        # Follow Docker best practices and assign a tag
        self.image = kwargs.get('image')
        # Specify a host to deploy the challenge onto.
        # The currently supported URI schemes are ssh:// and registry://
        # ssh is an ssh URI where the above image will be copied to and deployed (e.g. ssh://root@123.123.123.123)
        # registry is a Docker registry tag (e.g registry://registry.example.com/test/image)
        # host can also be specified during the deploy process: `ctf challenge deploy challenge --host=ssh://root@123.123.123.123`
        self.host = kwargs.get("host")
        # connection_info is used to provide a link, hostname, or instructions on how to connect to a challenge
        self.connection_info = kwargs.get("connection_info")
        # list of strings, each a challenge name to be completed before this one is allowed
        self.requirements = kwargs.get('requirements')
        if self.attempts:
            self.jsonpayload["max_attempts"] = self.attempts
        if self.connection_info:
            self.jsonpayload["connection_info"] = self.connection_info

        #return the newly created challenge instance
        return self
        #super().__init__()

    def _processhandout(self):
        '''
        TODO: scan for .tar.gz or folder
                - upload 
        '''

    def sync(self):
        '''
        These are the Actions that a Challenge folder can undergo, namely:

        Add:
            Adds a challenge to CTFd server
        Remove:
            Removes a challenge from CTFd server
        Delete:
            Deletes a challenge from the local Repository
        Write:
            Writes a challenge to the local Repository
        
        '''
        greenprint(f"Syncing challenge: {self.name}")
        try:
            #make API call
            apihandler = APIHandler()
            self.processchallenge(apihandler,self.jsonpayload)
        except Exception:
            errorlogger("[-] Error syncing challenge: API Request was {}".format(self.jsonpayload))

    def processchallenge(self,apihandler:APIHandler,jsonpayload:dict):
        try:
            # Create new flags
            if self.flags:
                apihandler.processflags(self,self.id,jsonpayload)
            # Update topics
            if self.topics:
                apihandler.processtopics(self,self.id,jsonpayload)
            # Update tags
            if self.tags:
                apihandler.processtopics(self,self.id,jsonpayload)
            # Upload files
            if self.files:
                apihandler.uploadfiles(self,self.id,jsonpayload)
            # Create hints
            if self.hints:
                apihandler.processhints(self,self.id,jsonpayload)
            # Update requirements
            if self.requirements:
                apihandler.processrequirements(self,self.id,jsonpayload)
        except Exception:
            errorlogger("[-] Error in Challenge.processchallenge()")

    def create(self,
               connection_info,
               attempts,
               max_attempts,
               value,
               dynamic,
               initial,
               decay,
               minimum,
               name,
               category,
               description,
               author,
               flags,
               topics,
               tags,
               hints,
               files,
               requirements
    ):
        '''
        host@server$> python ./ctfcli/ ctfcli ctfdops repo <category name> challenge create
        Creates a Manually crafted Challenge from supplied arguments
        on the command line

        Not Implemented yet
        '''
        self.id = 1
        self.type = type
        self.name = name
        self.description = description
        self.value = value
        #if its a dynamic scoring
        self.dynamic = dynamic
        self.initial = initial
        self.decay = decay
        self.minimum = minimum
        self.solved_by_me = "false"
        self.category = category
        self.tags = tags
        self.attempts = attempts
        self.connection_info = connection_info

        self.jsonpayload = {}
        if self.attempts:
            self.jsonpayload["max_attempts"] = self.max_attempts
        if connection_info:
            self.jsonpayload["connection_info"] = self.connection_info
        # Some challenge types (e.g. dynamic) override value.
        # We can't send it to CTFd because we don't know the current value
        if self.dynamic == True:
            self.scorepayload = {
                        'extra': {
                            'initial': self.initial,
                            'decay'  : self.decay,
                            'minimum': self.minimum
                            }
                        }
        elif self.dynamic == False:
            self.scorepayload = {'value':value}
            self.jsonpayload = {
                "name":         self.name,
                "category":     self.category,
                "description":  self.description,
                "type":         self.type,
                **self.scorepayload,
                "author" :      self.author
                }
        greenprint(f"Syncing challenge: {self.name}")
        try:
            #make API call
            apihandler = APIHandler()
            self.processchallenge(apihandler,self.jsonpayload)
        except Exception:
            errorlogger("[-] Error syncing challenge: API Request was {}".format(self.jsonpayload))

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
    
    def __repr__(self):
        '''
        The way it looks when you print to screen via the following method
        >>> asdf = Category(categoryfolderpath)
        >>> print(asdf)
        >>> 'Categoryname : <name>'
        >>> 'Challenges  : <challenge number>'
        >>> 'Number synched : <ctfd challenges in category>'
        '''
        numberofchallenges = len(self.listchallenges)
        self_repr = f"""Category: {self.name}
        Category Folder Location: {self.location}
        Number of Challenges in Category: {numberofchallenges}
        Number of Challenges Synched to CTFd Server: {self.getsynchedchallenges()}
        """
        return self_repr

    def _addchallenge(self, challenge:Challengeyaml):
        """
        Adds a challenge to the repository, appended to Category() class

        Args:
            challenge (Challenge): Challenge() object from folder in repository
        """
        try:    
            setattr(challenge.category,challenge.name,challenge)
        except:
            errorlogger(f"[-] Category._addchallenge failed with {challenge.category}")

    def _removechallenge(self, challengename):
        '''
        Removes a Challenge from the repository class

        Args:
            challengename (str): The name of the challenge as given by category.listchallenges()
                                 will fit the form "Challenge_SHA256HASHSTRING"
        '''
        delattr(self,challengename)
    
    def listchallenges(self):
        '''
        Lists all the challenges appended to this category
        '''

###############################################################################
#  Handout folder
###############################################################################
class Hando():
    '''
    LOL how do you like THIS name?!?
    muahaha
    '''
    #def __new__(cls,*args, **kwargs):
    def __new__(cls,**kwargs):
        cls.__name__ = "Handout"
        cls.__qualname__= 'Handout'
        cls.tag = '!Handout'
        return super().__new__(cls)
        #return super(cls).__new__(cls, *args, **kwargs)

class Handout(Hando):
    """
    Represents a Handout folder for files and data to be given to the
    CTF player
    """
    def __init__(self,**entries): 
        self.__dict__.update(entries)

###############################################################################
#  Solution folder
###############################################################################
class Soluto():
    '''
    OR THIS!?!? muhahahaAHAHAHA

    '''
    #def __new__(cls,*args, **kwargs):
    def __new__(cls,**kwargs):
        cls.__name__ = "Solution"
        cls.__qualname__= 'Solution'
        cls.tag = '!Solution'
        return super().__new__(cls)
        #return super(cls).__new__(cls, *args, **kwargs)

class Solution(Soluto):
    """
    Represents a Solution folder for data describing the methods and 
    steps necessary to solve the challenge and capture the flag
    """
    def __init__(self,**entries): 
        self.__dict__.update(entries)