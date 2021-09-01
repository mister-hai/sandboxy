import requests
import subprocess
from Yaml import Yaml
from pathlib import Path

from apicalls import APISession
from ctfdrepo import SandboxyCTFdRepository
from utils import errorlogger,yellowboldprint,greenprint

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
        #if its a dynamic scoring
        self.dynamic = bool
        self.description = str
        self.value = int
        self.solves = int
        self.solved_by_me = "false"
        self.category = str
        self.tags = []
        self.template = str
        self.script =  str
    

class ChallengeActions(Challenge):

    def sync(self):
        '''
        Adds a challenge to CTFd server
        
        '''
        greenprint(f"Syncing challenge: {self.name}")

        try:
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

                jsonpayload = {
                "name":         self.name,
                "category":     self.category,
                "description":  self.description,
                "type":         self.type,
                "value" :       self.value,
                "author" :      self.author
                }
            if self.attempts:
                jsonpayload["max_attempts"] = self.attempts
            if self.connection_info:
                jsonpayload["connection_info"] = self.connection_info
            try:
                #make API call
                apicall = APISession(prefix_url=self.CTFD_URL)
                # auth to server
                apicall.headers.update({"Authorization": "Token {}".format(apicall.AUTHTOKEN)})
                # check for challenge install
                apisess = apicall.get("/api/v1/challenges/{}".format(self.id), json=jsonpayload).json()["data"]
                # use requests.patch() to modify the value of a specific field on an existing APIcall.
                # why are they patching the challenge ID?
                response = apisess.patch(f"/api/v1/challenges/{self.id}", json=jsonpayload)
                response.raise_for_status()
            except requests.exceptions.HTTPError as errh:
                print(errh)
            except requests.exceptions.ConnectionError as errc:
                print(errc)
            except requests.exceptions.Timeout as errt:
                print(errt)
            except requests.exceptions.RequestException as err:
                print(err)
            # Create new flags
            if self.flags:
                apicall.processflags(challenge,self.id,jsonpayload)
            # Update topics
            if self.topics:
                apicall.processtopics(challenge,self.id,jsonpayload)
            # Update tags
            if self.tags:
                apicall.processtopics(challenge,self.id,jsonpayload)
            # Upload files
            if self.files:
                apicall.uploadfiles(challenge,self.id,jsonpayload)
            # Create hints
            if self.hints:
                apicall.processhints(challenge,self.id,jsonpayload)
            # Update requirements
            if self.requirements:
                apicall.processrequirements(challenge,self.id,jsonpayload)

            #if challenge.get["state"] =="visible":
        except Exception:
            errorlogger("[-] ERROR! FAILED TO SYNCRONIZE CHALLENGE WITH SERVER")

    def create(self, challenge, ignore=[]):
        jsonpayload = {
                "name":         self.name,
                "category":     self.category,
                "description":  self.description,
                "type":         {self.type", "standard"},
                "value":        int(challenge["value"]) if challenge["value"] else challenge["value"],
                **challenge.get("extra", {})
                }
        # Some challenge types (e.g. dynamic) override value.
        # We can't send it to CTFd because we don't know the current value
        if challenge["value"] is None:
            del challenge["value"]
        if self.attempts:
            jsonpayload["max_attempts"] = self.attempts
        if self.connection_info:
            jsonpayload["connection_info"] = self.connection_info
    
        apicall = APISession()
        response = apicall.post("/api/v1/challenges", json=jsonpayload)
        response.raise_for_status()
        challenge_data = response.json()
        self.id = challenge_data["data"]["id"]
        # Create flags
        if self.flags:
            apicall.processflags(challenge, challenge_id, jsonpayload)
        # Create topics
        if self.topics:
            apicall.processtopics(challenge, challenge_id, jsonpayload)
            # Create tags
        if self.tags:
            apicall.processtags(challenge,challenge_id,jsonpayload)
            # Upload files
        if self.files:
            apicall.uploadfiles(challenge,challenge_id,jsonpayload)
        # Add hints
        if self.hints:
            apicall.processhints()
        # Add requirements
        if self.requirements and "requirements" not in ignore:
            apicall.processrequirements(challenge,challenge_id,jsonpayload)
        # Set challenge state
        if self.state:
                jsonpayload["state"] = challenge["state"]
                apicall.makevisible(challenge)
                response.raise_for_status()


