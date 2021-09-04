from utils.apisession import APIHandler
from utils.utils import errorlogger,greenprint,CATEGORIES

class ChallengeFolder(): #folder
    '''
    Represents a Challenge Folder
        If the folder contents are not to specification
        The program will throw an error and refuse to process that folder

    '''
    def __init__(self, category, location, challengefile, handout, solution):
        if category not in CATEGORIES:
            errorlogger("[-] Inconsistancy in challenge.yml, \
                This field should be a Category in approved list {}".format(category))
        else:
            self.category= category
        # path to challenge folder
        self.challengelocation  = location
        # path to challenge.yml file
        self.challengefile = challengefile
        # folder
        self.solutiondir = solution
        # folder
        self.handout = handout
        # folder
        #self.challengesrc       = challengesrc
        #self.deployment         = deployment
        self.id = 1
        self.type = str
        self.internalname = hashlib.sha256(self.name)
        self.description = str
        self.value = int
        #if its a dynamic scoring
        self.dynamic = bool
        self.solves = int
        self.solved_by_me = "false"
        self.category = str
        self.tags = []
        self.template = str
        self.script =  str
        self.attempts = int
        self.connection_info = str
        # list of strings, each a challenge name to be completed before this one is allowed
        self.requirements = []
        self.jsonpayload = {}
        if self.attempts:
            self.jsonpayload["max_attempts"] = self.attempts
        if self.connection_info:
            self.jsonpayload["connection_info"] = self.connection_info
        # Some challenge types (e.g. dynamic) override value.
        # We can't send it to CTFd because we don't know the current value
        if self.dynamic == True:
            self.scorepayload = {
                        'extra': {
                            'initial': 500,
                            'decay'  : 100,
                            'minimum': 50
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


class ChallengeActions(Challenge):

    def sync(self):
        '''
        Adds a challenge to CTFd server
        
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
        host@server$> ctfops challenge create
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


