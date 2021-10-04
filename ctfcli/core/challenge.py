from hashlib import sha1
from logging import debug
from ctfcli.utils.utils import errorlogger,yellowboldprint,greenprint
from ctfcli.core.apisession import APIHandler
from ctfcli.utils.utils import redprint,DEBUG
from ctfcli.utils.utils import debugblue,debuggreen,debugred,debugyellow

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
        self.basepayload = {}
        self.secondarypayload = {}
        # set base challenge information
        debuggreen("[DEBUG] setting challenge information challenge class before API call")
        baselist = ["name","category","description","typeof","state"]
        for each in baselist:
            try:
                basevalue = getattr(self,each)
                self.basepayload.update({each:basevalue})
            except:
                pass
        #######################################################
        # shitty hack to undo the name change from            #
        # "type" to "typeof" for avoiding any bullshit        #
        # with python                                         #
        typeofchallengescore = self.basepayload.pop("typeof") #
        self.basepayload.update({"type":typeofchallengescore})#
        #######################################################
        # set score payload in base challenge information
        debugblue(f"[DEBUG] {self.basepayload}")
        if self.typeof == 'dynamic':
            self.scorepayload = {
                                'value'  : self.value,
                                'initial': self.initial,
                                'decay'  : self.decay,
                                'minimum': self.minimum
                                }
        elif (self.typeof == 'standard') or (self.typeof == 'static'):
            self.scorepayload = {'value' : self.value}
           #pass
        debuggreen("[DEBUG] Appending score payload to base payload")
        self.basepayload.update(self.scorepayload)# = {
        debugblue(f"[DEBUG] {self.basepayload}")
        # set secondary payload in base challenge information
        # the rest of the challenge information
        secondarypayload = ["connection_info","flags","topics","tags","hints","requirements","max_attempts"]
        for each in secondarypayload:
            try:
                secondaryvalue = getattr(self,each)
                self.secondarypayload.update({each:secondaryvalue})
            except:
                pass
        #    "name":            self.name,
        #    "category":        self.category,
        #    "description":     self.description,
        #    "type":            self.typeof,
        #    **self.scorepayload,
        #    #"value":           self.value,
        #    "state":           self.state,
        #    }
        #self.jsonpayload = {
        #    'flags':self.flags,
        #    'topics':self.topics,
        #    'tags':self.tags,
        #3    'files':self.files,
        #    'hints':self.hints,
        #    'requirements':self.requirements
        #}
        # Some challenge types (e.g. dynamic) override value.
        # We can't send it to CTFd because we don't know the current value
        #if self.value is None:
        #    del self.jsonpayload['value']

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
            errorlogger(f"[-] Error syncing challenge: {self.jsonpayload}")

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
