import json
from requests import Session
from ctfcli.utils.utils import errorlogger
#from utils.apifunctions import APIFunctions


class APIHandler():
    """
    Handler for the APISession() class
        Provides a wrapper for the API Functions
    
    Args: 
        ctfdurl (str): The URL of the CTFd Server instance you are operating
        authtoken (str): The authentication Token given in the settings page of the admin panel on the CTFd server
    """
    def __init__(self, ctfdurl,authtoken):
        self.ctfdurl = ctfdurl
        self.authtoken = authtoken
        self.APIPREFIX = "/api/v1/"
        self.CTFd_API_ROUTES = {"challenges": f"{self.APIPREFIX}challenges",
              "tags":f"{self.APIPREFIX}tags", 
              "topics":f"{self.APIPREFIX}topics", 
              "awards":f"{self.APIPREFIX}awards", 
              "hints":f"{self.APIPREFIX}hints", 
              "flags":f"{self.APIPREFIX}flags", 
              "submissions":f"{self.APIPREFIX}submissions", 
              "scoreboard":f"{self.APIPREFIX}scoreboard", 
              "teams":f"{self.APIPREFIX}teams", 
              "users":f"{self.APIPREFIX}users", 
              "statistics":f"{self.APIPREFIX}statistics",
              "files":f"{self.APIPREFIX}files", 
              "notifications":f"{self.APIPREFIX}notifications", 
              "configs":f"{self.APIPREFIX}configs", 
              "pages":f"{self.APIPREFIX}pages", 
              "unlocks":f"{self.APIPREFIX}unlocks", 
              "tokens":f"{self.APIPREFIX}tokens", 
              "comments":f"{self.APIPREFIX}comments"}
     

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

    def processrequirements(self, data):
        """
        Use a PATCH request to modify the Challenge Requirements
        """

    def processtags(self, data):
        '''
        Processes tags for the challenges
        '''

    def deleteremotehints(self,challenge_id,data):
        """
        deletes all hints from ctfd
        HARD MODE: ON
        """

    def processhints(self, data):
        '''
        process hints for the challenge
        '''

    def processtopics(self, data):
        '''
        process hints for the challenge
        '''
    def processflags(self, data):
        '''
        process hints for the challenge
        '''
    def uploadfiles(self,data):
        """
        uploads files to the ctfd server
        """

    def deleteremotefiles(self,file_path,data):
        """
        deletes files from ctfd server
        """


class APISession(Session):
    def __init__(self, *args, **kwargs):
        """
        Represents a connection to the CTFd API

        Args:
            
        """
        # auth to server
        self.headers.update({"Authorization": "Token {}".format(self.AUTHTOKEN)})

    def checkforchallenge(self, endpoint, jsonpayload):
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
    
    def handleresponse(self, response:dict):
        '''
        handles response
        '''
        template = {"data": [
            {
                "id": 3,
                "type": "multiple_choice",
                "name": "Trivia",
                "value": 42,
                "solves": 4,
                "solved_by_me": 'false',
                "category": "Multiple Choice",
                "tags": [],
                "template": "/plugins/multiple_choice/assets/view.html",
                "script": "/plugins/multiple_choice/assets/view.js"
            }]
        }
    def was_there_was_an_error(self, responsecode):
        """ Returns False if no error"""
        # server side error]
        set1 = [404,504,503,500]
        set2 = [400,405,501]
        set3 = [500]
        if responsecode in set1 :
            errorlogger("[-] Server side error - No Resource Available in REST response - Error Code {}".format(responsecode))
            return True # "[-] Server side error - No resource Available in REST response"
        if responsecode in set2:
            errorlogger("[-] User error in Request - Error Code {}".format(responsecode))
            return True # "[-] User error in Image Request"
        if responsecode in set3:
            #unknown error
            errorlogger("[-] Unknown Server Error - No Resource Available in REST response - Error Code {}".format(responsecode)) 
            return True # "[-] Unknown Server Error - No Image Available in REST response"
        # no error!
        if responsecode == 200:
            return False

            #except requests.exceptions.HTTPError as errh:
            #    print(errh)
            #except requests.exceptions.ConnectionError as errc:
            #    print(errc)
            #except requests.exceptions.Timeout as errt:
            #    print(errt)
            #except requests.exceptions.RequestException as err:
            #    print(err)