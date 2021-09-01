import requests
import subprocess
from pathlib import Path

from utils.Yaml import Yaml
from utils.apisession import APISession
from utils.apisession import APIHandler
from utils.ctfdrepo import SandboxyCTFdRepository
from utils.utils import errorlogger,yellowboldprint,greenprint,CATEGORIES

class Challenge(): #folder
    '''
    Represents a Challenge Folder
        If the folder contents are not to specification
        The program will throw an error and refuse to process that folder

    '''
    def __init__(self, 
                name,
                category,
                location, 
                challengefile, 
                #challengesrc,
                #deployment,
                handout,
                solution
                ):
        self.name               = str
        if category not in CATEGORIES:
            errorlogger("[-] Inconsistancy in challenge.yml, \
                This field should be a Category in approved list {}".format(category))
        else:
            self.category           = category
        # path to challenge folder
        self.challengelocation  = location
        # path to challenge.yml file
        self.challengefile      = challengefile
        # folder
        self.solutiondir        = solution
        # folder
        self.handout            = handout
        # folder
        #self.challengesrc       = challengesrc
        #self.deployment         = deployment
        self.id = 1
        self.type = str
        self.name = str
        self.description = str
        self.value = int
        #if its a dynamic scoring
        self.dynamic = bool
        #self.extra = {
        #            'extra':{
        #                    'initial':500,
        #                    'decay'  :100,
        #                    'minimum':50
        #                    }
        #            }
        self.solves = int
        self.solved_by_me = "false"
        self.category = str
        self.tags = []
        self.template = str
        self.script =  str
        self.attempts = int
        self.connection_info = str
        jsonpayload = {}
        if self.attempts:
            jsonpayload["max_attempts"] = self.attempts
        if self.connection_info:
            jsonpayload["connection_info"] = self.connection_info
        # Some challenge types (e.g. dynamic) override value.
        # We can't send it to CTFd because we don't know the current value
        if self.dynamic == True:
            scorepayload = {
                        'extra': {
                            'initial': 500,
                            'decay'  : 100,
                            'minimum': 50
                            }
                        }
        elif self.dynamic == False:
            scorepayload = {'value':self.value}
            jsonpayload = {
                "name":         self.name,
                "category":     self.category,
                "description":  self.description,
                "type":         self.type,
                **scorepayload,
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
    
    def processchallenge(self,apihandler:APIHandler,jsonpayload:dict):
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
            errorlogger("[-] ERROR! FAILED TO SYNCRONIZE CHALLENGE WITH SERVER")

    def create(self, challenge, ignore=[]):
        jsonpayload = {
                "name":         self.name,
                "category":     self.category,
                "description":  self.description,
                "type":         {self.type, "standard"},
                "value":        self.value,
                "extra":        self.extra
                }
        # Some challenge types (e.g. dynamic) override value.
        # We can't send it to CTFd because we don't know the current value
        if challenge["value"] is None:
            del challenge["value"]
        if self.attempts:
            jsonpayload["max_attempts"] = self.attempts
        if self.connection_info:
            jsonpayload["connection_info"] = self.connection_info
    
        apihandler = APISession()
        response = apihandler.post("/api/v1/challenges", json=jsonpayload)
        response.raise_for_status()
        challenge_data = response.json()
        self.id = challenge_data["data"]["id"]
        # Create flags
        if self.flags:
            apihandler.processflags(jsonpayload)
        # Create topics
        if self.topics:
            apihandler.processtopics(jsonpayload)
            # Create tags
        if self.tags:
            apihandler.processtags(jsonpayload)
            # Upload files
        if self.files:
            apihandler.uploadfiles(jsonpayload)
        # Add hints
        if self.hints:
            apihandler.processhints()
        # Add requirements
        if self.requirements:
            apihandler.processrequirements(jsonpayload)
        # Set challenge state
        #if self.state:
        #        jsonpayload["state"] = challenge["state"]
        #        apihandler.makevisible(challenge)
        #        response.raise_for_status()


