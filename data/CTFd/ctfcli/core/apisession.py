import requests
from ctfcli.core.APICore import APICore
from ctfcli.utils.utils import errorlog, greenprint

class APIHandler(APICore):
    """
    Handler for the APISession() class
        Provides a wrapper for the API Functions
        
        This is NOT designed with an asynchronous focus
        
        This IS stateful
            the class attributes will reflect the operation in progress. 
            Thread this operation if you need asynchronous functionality

        Process:

            base challenge is created on server
                returns a challenge ID
                apply that ID to the challenge for the masterlist
                use that ID for the processing of
            - tags
            - topics
            - requirements
            - flags
            - files
            - visibility
        
        for dev use:
        useragent = 'Mozilla/5.0 (X11; Linux x86_64; rv:28.0) Gecko/20100101  Firefox/28.0'
    Args: 
        ctfdurl (str): The URL of the CTFd Server instance you are operating
        authtoken (str): The authentication Token given in the settings page of the admin panel on the CTFd server
    """
    def __init__(self, ctfdurl,authtoken):
        #https://server.host.net/ctfd/
        self.ctfdurl = ctfdurl
        self.authtoken = authtoken

    def getusers(self):
        """ gets a list of all users"""


    def getsyncedchallenges(self):
        """
        Gets a json container of all the challenges synced to the server
        This is step one for any procedure modifying challenges
        We cant discern if a challenges attributes have been modified on the
        server by an administrator or a hacker
        """
        endpoint = self._getroute('challenges') + "?view=admin"
        return self.getrequest(url = endpoint, json=True).json()["data"]

    def _createbasechallenge(self):
        """
        Creates the initial challenge entry, to be 
        updated with relevant additional information
        used during a session
        STEP 3 overall
        step 1 in challenge creation
        POST /api/v1/challenges HTTP/1.1
        """
        # happens first
        # create new challenge
        self.apiresponse = self.apisession.post(url=self._getroute('challenges'), 
                                                json=self.challengetemplate,
                                                allow_redirects=True)
        # original code
        #r = s.post("/api/v1/challenges", json=data)
        self.apiresponse.raise_for_status()
        self.challenge_data = self.apiresponse.json()
        self.challenge_id = self.challenge_data["data"]["id"]

        ##############################################################
        # Everything below happens AFTER the challenge is created
        ##############################################################

    def _process(self,tag:str,jsonpayload:dict):
        """
        Uploads/sets sattributes on challenge on server after initial creation
        of the challenge entry

        Some challenges may have more or less information to sync depending
        on the challenge creators intents and designs
        """
        # Create new flags
        if tag == 'flags':
            self._processflags(self.challenge_id,jsonpayload)
        # Update topics
        if tag == 'topics':
            self._processtopics(self.challenge_id,jsonpayload)
        # Update tags
        if tag == 'tags':
            self._processtopics(self.challenge_id,jsonpayload)
        # Upload files
        if tag == 'files':
            self._uploadfiles(self.challenge_id,jsonpayload)
        # Create hints
        if tag == 'hints':
            self._processhints(self.challenge_id,jsonpayload)
        # Update requirements
        if tag == 'requirements':
            self._processrequirements(self.challenge_id,jsonpayload)

    def _processrequirements(self, challengeid:int, jsonpayload:dict) -> requests.Response:
        """
        Use a PATCH request to modify the Challenge Requirements
        This is done towards the end
        """
        required_challenges = []
        for requirements in jsonpayload.get("requirements"):
            # if the requirements are other challenges
            if type(requirements) == str:
                required_challenges.append(challengeid)
            # if the requirement is a score value
            elif type(requirements) == int:
                required_challenges.append(requirements)
        required_challenges = list(set(required_challenges))
        data = {"requirements": {"prerequisites": required_challenges}}
        apiresponse = self.patch(self._getroute('challenges') + str(challengeid), json=data)
        apiresponse.raise_for_status()

    def _processtags(self, challengeid:int, jsonpayload:dict) -> requests.Response:
        '''
        Processes tags for the challenges
        '''
        #if jsonpayload.get("tags"):
        for tag in jsonpayload.get("tags"):
            apiresponse = self.post(
                    self._getroute('tags'), 
                    json={
                        "challenge_id": challengeid,
                        "value": tag
                        }
                    )
            apiresponse.raise_for_status()

    def _processhints(self,hints, challengeid:int, hintcost:int):
        '''
        process hints for the challenge
        Hints are used to give players a way to buy or have suggestions. They are not
        required but can be nice.
        Can be removed if unused
        Accepts dictionaries or strings
        >>> self.hints = kwargs.get("hints")
        #    - {
        #        content: "This hint costs points",
        #        cost: 10
        #    }
        #    - This hint is free
        '''
        for hint in hints:
            if type(hint) == str:
                self.hintstemplate["content"] = hint
                self.hintstemplate["cost"] = hintcost
                self.hintstemplate["challenge_id"] = challengeid
            else:
                self.hintstemplate["content"] = hint["content"]
                self.hintstemplate["cost"] = hint["cost"]
                self.hintstemplate["challenge_id"] = challengeid
            #make request with hints template
            self.apiresponse = self.post(self._getroute('hints'), json=self.hintstemplate)
            self.apiresponse.raise_for_status()

    def _processtopics(self, jsonpayload:dict):
        '''
        process hints for the challenge
        '''
        for topic in jsonpayload.get("topics"):
            self.topictemplate['value'] = topic
            self.apiresponse = self.post(self._getroute("topics"),json=self.topictemplate)
            self.apiresponse.raise_for_status()

    def _processflags(self, challengeid:int, jsonpayload:dict) -> requests.Response:
        '''
        process hints for the challenge
        '''
        for flag in jsonpayload.get("flags"):
                if type(flag) == str:
                    self.flagstemplate["content"] = flag
                    self.flagstemplate["type"] = "static"
                    self.flagstemplate["challenge_id"] = challengeid
                    self.apiresponse = self.post(self._getroute("flags"), json=self.flagstemplate)
                    self.apiresponse.raise_for_status()
                elif type(flag) == dict:
                    self.flagstemplate["challenge_id"] = challengeid
                    self.apiresponse = self.post(self._getroute("flags"), json=flag)
                    self.apiresponse.raise_for_status()

    def _uploadfiles(self, file):
        """
        uploads files to the ctfd server
        Only the handout.tar.gz should be uploaded as of now

        Args:
            file (TarFile): The file to upload to accompany the challenge
        """
        data = {"challenge_id": self.challenge_id, "type": "challenge"}
        # Specifically use data= here instead of json= to send multipart/form-data
        self.apiresponse = self.post(url = self._getroute('files'), files=file, data=data)
        self.apiresponse.raise_for_status()

