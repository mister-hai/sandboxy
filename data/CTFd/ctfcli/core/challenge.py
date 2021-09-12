import os
from hashlib import sha256
from pathlib import Path
from requests import Response
from ctfcli.core.yamlstuff import Yaml
from ctfcli.utils.utils import errorlogger, CATEGORIES,yellowboldprint,greenprint
from ctfcli.core.apisession import APIHandler
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
            handout,
            solution,
            readme
            ):
        self.folderlocation  = Path(os.path.abspath(challengeyaml))
        self.challengefile = challengeyaml
        self.solutiondir = solution
        self.handout = handout
        self.readme = readme
        self.tag = "!Challenge:"

        # this is set after syncing by the ctfd server, it increments by one per
        # challenge upload so it's predictable
        self.id = int
        if category not in CATEGORIES:
            errorlogger("[-] Inconsistancy in inputs {}".format(category))
        else:
            self.category = category
        #get a representation of the challenge.yaml file
        yamlcontents = self.loadyaml(self.challengefile)
        #load the challenge yaml dict into the class
        self._initchallenge(**yamlcontents)
        # unpack supplied dict
        #self.__dict__.update(entries)
        # the new classname is defined by the name tag in the Yaml now
        self.internalname = "Challenge_" + str(sha256(self.name.encode("ascii")).hexdigest())
        self.__name = self.internalname
        self.__qualname__ = self.internalname
        yellowboldprint(f'[+] Internal name: %s' % self.internalname)
        #self.challengesrc       = challengesrc
        #self.deployment         = deployment

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
            self.author = kwargs.pop('author')
            self.description = kwargs.pop('description')
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
                pass
        except Exception:
            errorlogger('[-] ERROR: No flag in challenge')
            pass
        
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
        # OLD COMMENT
        # Some challenge types (e.g. dynamic) override value.
        # We can't send it to CTFd because we don't know the current value
        if type(kwargs.get('value')) != int:
            raise TypeError
        else:
            self.value = kwargs.pop('value')
        self.typeof = kwargs.pop('type')
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

    def __repr__(self):
        '''
        printself
        '''
        for key in self.__dict__:
            print(str(key) + " : " + str(self.__dict__[key]))

    def _setpayload(self):
        """
        Set the json_payload variable for interacting with the CTFd API
        This is the /challenge endpoint template
        """
        if self.typeof == 'dynamic':
            self.scorepayload['extra'] = {
                                'initial': self.extra['initial'],
                                'decay'  : self.extra['decay'],
                                'minimum': self.extra['minimum']
                                }
        elif (self.typeof == 'standard') or (self.typeof == 'static'):
            #self.jsonpayload['value'] = self.value
            pass
        # set final payload
        self.jsonpayload = {
            "name":            self.name,
            "category":        self.category,
            "author" :         self.author,
            "description":     self.description,
            "type":            self.type,
            "value":           self.value,
            "state":           self.state,
            #"max_attempts":    self.attempts,
            #"connection_info": self.connection_info,
            # unpack "value + extra" OR "value"
            **self.scorepayload
            }
        #self.jsonpayload["state"] = "visible"
        # Some challenge types (e.g. dynamic) override value.
        # We can't send it to CTFd because we don't know the current value
        #if self.value is None:
        #    del self.jsonpayload['value']
        if self.attempts:
            self.jsonpayload["max_attempts"] = self.attempts
        if self.connection_info and self.connection_info:
            self.jsonpayload['connection_info'] = self.connection_info

    def _processhandout(self):
        '''
        TODO: scan for .tar.gz or folder
                - upload 
        '''

    def sync(self, apihandler: APIHandler):
        '''
        Add(sync):
            Adds a challenge to CTFd server

        Args:
            apihandler (APIHandler): APIHandler class, instances a Requests.Session to CTFd url
        '''
        greenprint(f"Syncing challenge: {self.name}")
        try:
            #make API call
            #apihandler = APIHandler()
            # create initial entry in CTFd Server to get a challenge ID
            # the challenge ID is necessary for later
            self._setpayload()
            # set auth headers with token
            apihandler._apiauth()
            # send request
            apiresponse = apihandler.postrequest('challenges',self.jsonpayload)

            apiresponse.raise_for_status()
            # TODO: get return value for challenge id from a 
            # list synced challenges
            # after syncing everything and then sort by name
            challengeid = apihandler
            self.processchallenge(apihandler,self.jsonpayload)
            self.id = challengeid
        except Exception:
            errorlogger("[-] Error syncing challenge: API Request was {}".format(self.jsonpayload))

    def _getid(self, apiresponse:Response):
        """
        Gets data from API
        mirror api response structure
        """
        response = apiresponse.json()['data']
        for challenge in response:
            challengeid = challenge.get('id')
            typeof = challenge.get('type')
            name = challenge.get('name')
            value = challenge.get('value')
            solves = challenge.get('solves')
            solved_by_me = challenge.get('solved_by_me')
            category = challenge.get('category')
            tags = challenge.get('tags')
            template = challenge.get('template')
            script = challenge.get('script')
            


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
