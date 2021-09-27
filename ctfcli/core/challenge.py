import os
from hashlib import sha1
from pathlib import Path
from tarfile import TarFile
import tarfile
from ctfcli.core.yamlstuff import Yaml
from ctfcli.utils.utils import errorlogger,yellowboldprint,greenprint
from ctfcli.utils.utils import redprint
from ctfcli.core.apisession import APIHandler


###############################################################################
#  CHALLENGEYAML
###############################################################################
class Challenge():#Yaml):
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
