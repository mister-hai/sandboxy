import os
from hashlib import sha256
from pathlib import Path
from tarfile import TarFile
import tarfile
from ctfcli.core.yamlstuff import Yaml
from ctfcli.utils.utils import errorlogger,yellowboldprint,greenprint
from ctfcli.utils.utils import redprint
from ctfcli.core.apisession import APIHandler
from ctfcli.utils.utils import _processfoldertotarfile

###############################################################################
#  CHALLENGEYAML
###############################################################################
class Challenge(Yaml):
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
    >>> newchallenge = Challenge(filepath)

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
            category,
            challengeyaml,
            handout:Path,
            solution:Path,
            readme
            ):
        self.tag = "!Challenge:"
        self.readme = readme
        self.category = category
        self.challengefile = challengeyaml
        self.folderlocation  = Path(os.path.abspath(challengeyaml)).parent
        #get a representation of the challenge.yaml file
        yamlcontents = self.loadyaml(self.challengefile)
        #load the challenge yaml dict into the class
        self._initchallenge(**yamlcontents)
        # the new classname is defined by the name tag in the Yaml now
        self.internalname = "Challenge_" + str(sha256(self.name.encode("ascii")).hexdigest())
        self.__name = self.internalname
        self.__qualname__ = self.internalname
        yellowboldprint(f'[+] Internal name: {self.internalname}')
        #self.challengesrc       = challengesrc
        #self.deployment         = deployment
        self.solutionfolder =   Path(self.folderlocation, 'solution')
        self.handoutfolder =    Path(self.folderlocation, 'handout')
        self.solution = _processfoldertotarfile(folder = self.solutionfolder, filename = 'solution.tar.gz')
        self.handout  = _processfoldertotarfile(folder = self.handoutfolder, filename = 'handout.tar.gz')
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
        #Required sections get the "pop()" function 
        # a KeyError will be raised if the key does not exist
        try:
            self.name = kwargs.pop("name")
            #self.author = kwargs.pop('author')
            self.description = kwargs.pop('description')
        except Exception:
            errorlogger("[-] Challenge.yaml does not conform to specification, \
                rejecting. Please check the error log.")
        self.author = kwargs.get('author')
        #self.challengesrc = kwargs.get('challengesrc')
        #self.deployment   = kwargs.get('deployment')
        #self.description = kwargs.get('description')
        self.value = kwargs.get('value')
        # can be from masterfile or server, not challenge.yaml
        self.solves = int#kwargs.get('solves')
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
        ##############################################
        # FLAGS
        ##############################################
        # Flags specify answers that your challenge use. You should generally provide at least one.
        # Can be removed if unused
        # Accepts strings or dictionaries of CTFd API data
        #flags:
        #    # A static case sensitive flag
        #    - flag{3xampl3}
        #    # A static case sensitive flag created with a dictionary
        #    - {
        #        type: "static",
        #        content: "flag{wat}",
        #    }
        #    # A static case insensitive flag
        #    - {
        #        type: "static",
        #        content: "flag{wat}",
        #        data: "case_insensitive",
        #    }
        #    # A regex case insensitive flag
        #    - {
        #        type: "regex",
        #        content: "(.*)STUFF(.*)",
        #        data: "case_insensitive",
        #    }
        try:
            self.flags = kwargs.pop('flags')
        except Exception:
            try:
                self.flags = kwargs.pop('flag')
            except Exception:
                errorlogger('[-] ERROR: No flag in challenge')
                pass
        
        #if type(self.flags) == list:

        self.requirements = kwargs.get("requirements")
        #    - "Warmup"
        #    - "Are you alive"
        # The state of the challenge.
        # If the field is omitted, the challenge is visible by default.
        # If provided, the field can take one of two values: hidden, visible.
        if kwargs.get("state") != None:
            self.state = kwargs.get("state")
        else:
            self.state = "visible"
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
        # OLD COMMENT
        # Some challenge types (e.g. dynamic) override value.
        # We can't send it to CTFd because we don't know the current value
        if type(kwargs.get('value')) != int:
            raise TypeError
        else:
            self.value = kwargs.pop('value')

        # older versions have "static" as value for "standard"?
        self.typeof = kwargs.pop('type')
        if self.typeof == 'static':
            self.typeof = 'standard'
        # get extra field if exists
        if self.typeof == 'dynamic':
            self.extra = kwargs.pop("extra")
        #raise ValueError(f"Unknown type {typeof} in Classconstructor.Challenge._initchallenge()")
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
        self.attempts = kwargs.get('attempts')

        ################################
        # FILES
        ################################
        self.files = kwargs.get('files')
        return self
        # package handout if not already packaged
        #self._processhandout()
        #self.jsonpayload['handout'] = self.handout

    #def __repr__(self):
    #    '''
    #    printself
    #    '''
    #    for key in self.__dict__:
    #        print(str(key) + " : " + str(self.__dict__[key]))

    def _setpayload(self):
        """
        Set the json_payload variable for interacting with the CTFd API
        This is the /challenge endpoint template
        """
        if self.typeof == 'dynamic':
            self.scorepayload = {
                                'value'  : self.value,
                                'initial': self.extra['initial'],
                                'decay'  : self.extra['decay'],
                                'minimum': self.extra['minimum']
                                }
        elif (self.typeof == 'standard') or (self.typeof == 'static'):
            self.scorepayload = {'value' : self.value}
            #pass
        # set base challenge payload
        self.basepayload = {
            "name":            self.name,
            "category":        self.category,
            "description":     self.description,
            "type":            self.typeof,
            **self.scorepayload,
            #"value":           self.value,
            "state":           self.state,
            }
        # the rest of the challenge information
        self.jsonpayload = {
            'flags':self.flags,
            'topics':self.topics,
            'tags':self.tags,
            'files':self.files,
            'hints':self.hints,
            'requirements':self.requirements
        }
        # Some challenge types (e.g. dynamic) override value.
        # We can't send it to CTFd because we don't know the current value
        #if self.value is None:
        #    del self.jsonpayload['value']
        if self.attempts:
            self.jsonpayload["max_attempts"] = self.attempts
        if self.connection_info and self.connection_info:
            self.jsonpayload['connection_info'] = self.connection_info

    def sync(self, apihandler:APIHandler):
        '''
        Adds a challenge to CTFd server

        Args:
            apihandler (APIHandler): APIHandler class, instances a Requests.Session to CTFd url
        '''
        greenprint(f"Syncing challenge: {self.name}")
        try:
            # create initial entry in CTFd Server to get a challenge ID
            self._setpayload()
            # send request for base challenge creation
            apihandler._createbasechallenge(self.basepayload)
            # get challenge ID from Response and assign to self for later 
            # re-combination into the repository masterlist
            self.id = apihandler.challenge_id
            # process the rest of the challenge data
            self._processchallenge(apihandler)#,self.jsonpayload)
        except Exception:
            errorlogger(f"[-] Error syncing challenge: API Request was {self.jsonpayload}")

    def _processchallenge(self,apihandler:APIHandler):#,jsonpayload:dict):
        """
        Handles uploading the rest of the challenge information
        
        'flags''topics''tags''files''hints''requirements'
        
        """
        try:
            for each in ['flags','topics','tags','hints','requirements']:#'files',
                # hints
                if self.jsonpayload.get(each) != None:
                    apihandler._process(each,self.id,self.jsonpayload)
            # we are not providing solutions to the users by default
            if self.solution != None:
                pass
            if self.handout != None:
                apihandler._uploadfiles(self.id,self.handout)
        except Exception:
            print(each)
            print(self.jsonpayload.get(each))
            errorlogger("[-] Error in Challenge.processchallenge()")


    def getvisibility(self, challengeid, jsonpayload):
        """
        Gets the visibility of a challenge
        Hidden , Visible
        TODO: make it work
        """

    def togglevisibility(self, challenge):
        """
        Toggles a Challenge between hidden and visible
        """
    
    def makevisible(self,challenge,challenge_id):
        """
        Makes a Challenge Visible

        Args:
            challenge (str): The challenge to change state
        """

    def makehidden(self, challenge):
        """
        Makes a Challenge Hidden

        Args:
            challenge (str): The challenge to change state
        """

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
        ##assign all the variables to self via **kwargs
        greenprint(f"Syncing challenge: {self.name}")
        try:
            #make API call
            apihandler = APIHandler()
            self._processchallenge(apihandler,self.jsonpayload)
        except Exception:
            errorlogger("[-] Error syncing challenge: API Request was {}".format(self.jsonpayload))
