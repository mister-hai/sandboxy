import json
from pathlib import Path
from requests import Session
from utils import errorlogger,blueprint,yellowboldprint,redprint
from ctfdrepo import SandboxyCTFdRepository
from utils.apifunctions import APIFunctions


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
        """
        # auth to server
        self.headers.update({"Authorization": "Token {}".format(self.AUTHTOKEN)})

    def getrequest(self, jsonpayload:json):
        '''
        Performs a request to the CTFd server API
        '''
        # check for challenge install
        apisess = self.get("/api/v1/challenges/{}".format(self.id), json=jsonpayload).json()["data"]
        # use requests.patch() to modify the value of a specific field on an existing APIcall.
        response = apisess.patch(f"/api/v1/challenges/{self.id}", json=jsonpayload)
        response.raise_for_status()

    def postrequest(self):
        '''
        Makes a POST Request
        '''


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