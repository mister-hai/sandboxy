import json,yaml
import requests
from ctfcli.core.APICore import APICore
from ctfcli.utils.utils import errorlogger, errorlog, greenprint
#from utils.apifunctions import APIFunctions



class APIHandler(APICore):
    """
    Handler for the APISession() class
        Provides a wrapper for the API Functions

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

    def getsyncedchallenges(self):
        """
        Gets a json container of all the challenges synced to the server
        """
        self._apiauth()
        endpoint = self._getroute('challenges') + "?view=admin"
        return self.get(url = endpoint, json=True).json()["data"]

    def getusers(self):
        """ gets a list of all users"""

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

    def processrequirements(self, challengeid:int, jsonpayload:dict) -> requests.Response:
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

    def processtags(self, challengeid:int, jsonpayload:dict) -> requests.Response:
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

    def deleteremotehints(self,challenge_id,data):
        """
        deletes all hints from ctfd
        HARD MODE: ON
        """

    def processhints(self,hints, challengeid:int, hintcost:int):
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
            apiresponse = self.post(self._getroute('hints'), json=self.hintstemplate)
            apiresponse.raise_for_status()

    def processtopics(self, jsonpayload):
        '''
        process hints for the challenge
        '''
        for topic in jsonpayload.get("topics"):
            self.topictemplate['value'] = topic
            apiresponse = self.post(self._getroute("topics"),
                json= self.topictemplate)
            apiresponse.raise_for_status()

    def processflags(self, challengeid:int, jsonpayload:dict) -> requests.Response:
        '''
        process hints for the challenge
        '''
        for flag in jsonpayload.get("flags"):
                if type(flag) == str:
                    self.flagstemplate["content"] = flag
                    self.flagstemplate["type"] = "static"
                    self.flagstemplate["challenge_id"] = challengeid

                    apiresponse = self.post(f"/api/v1/flags", json=jsonpayload)
                    apiresponse.raise_for_status()
                elif type(flag) == dict:
                    flag["challenge"] = challengeid
                    apiresponse = self.post(f"/api/v1/flags", json=flag)
                    apiresponse.raise_for_status()

    def uploadfiles(self, jsonpayload) -> requests.Response:
        """
        uploads files to the ctfd server
        """
        if jsonpayload.get("files") and "files" not in ignore:
            files = []
            for f in jsonpayload.get("files"):
                file_path = Path(challenge.directory, f)
                if file_path.exists():
                    file_object = ("file", file_path.open(mode="rb"))
                    files.append(file_object)
                else:
                    click.secho(f"File {file_path} was not found", fg="red")
                    raise Exception(f"File {file_path} was not found")

            data = {"challenge_id": challenge_id, "type": "challenge"}
            # Specifically use data= here instead of json= to send multipart/form-data
            apiresponse = self.post(f"/api/v1/files", files=files, data=data)
            apiresponse.raise_for_status()

    def deleteremotefiles(self,file_path,data):
        """
        deletes files from ctfd server
        """


#class APISession(Session):
#    def __init__(self, *args, **kwargs):
#        """
#        Represents a connection to the CTFd API
#
#        Args:
#            
#        """
#        super(APISession, self).__init__(*args, **kwargs)


    def checkforchallenge(self, endpoint, jsonpayload):
        """
        ("/api/v1/challenges?view=admin", json=True
        """
        return self.get("{}{}".format(endpoint,self.id), json=jsonpayload).json()["data"]

    def getrequest(self, endpoint, jsonpayload:json):
        '''
        Performs GET request to the Specified Endpoint with jsonpayload['id']

        Args:
            endpoint (str): the API endpoint to send to , e.g. /api/vi/challenges
            payload  (str): the json payload required for the get request
        '''
        response = self.get("{}{}".format(endpoint,jsonpayload['id']), json=jsonpayload)
        response.raise_for_status()

    def postrequest(self, endpoint, jsonpayload:dict) -> requests.Response:
        '''
        Makes a POST Request to the Specified Endpoint

        Args:
            endpoint (str): the endpoint to send to , e.g. 'challenges'
            payload  (str): the json payload required for the post request
        '''
        response = self.post(url = self._getroute(endpoint), json=jsonpayload)
        return response

    def patchrequest(self, endpoint, jsonpayload:json):
        """
        Makes a Patch Request to the Specified Endpoint with jsonpayload['id']

        Args:
            endpoint (str): the API endpoint to send to , e.g. /api/vi/challenges
            payload  (str): the json payload required for the patch request
                            
        """
        response = self.patch("{}{}".format(endpoint,jsonpayload['id']), json=jsonpayload)
        response.raise_for_status()

    def deleterequest(self, endpoint, jsonpayload:json):
        '''
        Makes a Delete Request to the Specified Endpoint with jsonpayload['id']

        Args:
            endpoint (str): the API endpoint to send to , e.g. /api/vi/challenges
            payload  (str): the json payload required for the delete request
        '''
        response = self.delete("{}{}".format(endpoint,jsonpayload['id']), json=jsonpayload)
        response.raise_for_status()
    
