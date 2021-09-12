import json,yaml
#from requests import Session
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

    def _getroute(self, tag):
        """
        Gets API route string for Requests Session
        Args:
            tag (str): Route to send JSON/web request to
        """
        #dictofroutes = {}
        if tag in self.routeslist:
            #dictofroutes[tag] = f"{self.ctfdurl}{self.APIPREFIX}{tag}"
            return f"{self.ctfdurl}{self.APIPREFIX}{tag}" #dictofroutes

    def handleresponse(self, response:dict):
        '''
        handles response
        '''


    def getsyncedchallenges(self):
        """
        Gets a json container of all the challenges synced to the server
        """
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

    def processrequirements(self, jsonpayload):
        """
        Use a PATCH request to modify the Challenge Requirements
        This is done towards the end
        """
        syncedchallenges = self.getsyncedchallenges()
        required_challenges = []
        for requirements in jsonpayload.get("requirements"):
            # if the requirements are other challenges
            if type(requirements) == str:
                for challenge in syncedchallenges:
                        if jsonpayload.get("name") == requirements:
                            required_challenges.append(challenge["id"])
            # if the requirement is a score value
            elif type(requirements) == int:
                required_challenges.append(requirements)
        required_challenges = list(set(required_challenges))
        data = {"requirements": {"prerequisites": required_challenges}}
        apiresponse = self.patch(f"/api/v1/challenges/{challenge.id}", json=data)
        apiresponse.raise_for_status()

    def processtags(self, challengeid:int, jsonpayload:dict):
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

    def processhints(self, data):
        '''
        process hints for the challenge
        '''
        for hint in jsonpayload.get("hints"):
            if type(hint) == str:
                data = {"content": hint, "cost": 0, "challenge_id": challenge_id}
            else:
                data = {
                    "content": hint["content"],
                    "cost": hint["cost"],
                    "challenge_id": challenge_id,
                }
            apiresponse = self.post(self._getroute('hints'), json=data)
            apiresponse.raise_for_status()

    def processtopics(self, data):
        '''
        process hints for the challenge
        '''
        for topic in jsonpayload.get("topics"):
            self.topictemplate['value'] = topic
            apiresponse = self.post(self._getroute("topics"),
                json= self.topictemplate)
            apiresponse.raise_for_status()
    def processflags(self, data):
        '''
        process hints for the challenge
        '''
        if jsonpayload.get("flags") and "flags" not in ignore:
            for flag in jsonpayload.get("flags"):
                if type(flag) == str:
                    data = {"content": flag, "type": "static", "challenge_id": challenge_id}
                    apiresponse = self.post(f"/api/v1/flags", json=data)
                    apiresponse.raise_for_status()
                elif type(flag) == dict:
                    flag["challenge"] = challenge_id
                    apiresponse = self.post(f"/api/v1/flags", json=flag)
                    apiresponse.raise_for_status()

    def uploadfiles(self,data):
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

    def postrequest(self, endpoint, jsonpayload:json):
        '''
        Makes a POST Request to the Specified Endpoint with jsonpayload['id']

        Args:
            endpoint (str): the API endpoint to send to , e.g. /api/vi/challenges
            payload  (str): the json payload required for the post request
        '''
        response = self.post("{}{}".format(endpoint,jsonpayload['id']), json=jsonpayload)
        response.raise_for_status()

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
    
