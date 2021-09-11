import json,yaml
from requests import Session
from ctfcli.utils.utils import errorlogger, errorlog, greenprint
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
        #https://server.host.net/ctfd/
        self.ctfdurl = ctfdurl
        self.authtoken = authtoken
        self.APIPREFIX = "/api/v1/"
        self.routeslist = ["challenges","tags","topics","awards",
        "hints", "flags","submissions","scoreboard",
        "teams","users","statistics","files", "notifications",
        "configs", "pages", "unlocks", "tokens", "comments"]

    def _getroute(self, tag):
        """
        Gets API route string for Requests Session
        Args:
            tag (str): Route to send JSON/web request to
        """
        dictofroutes = {}
        if tag in self.routeslist:
            dictofroutes[tag] = f"{self.ctfdurl}{self.APIPREFIX}{tag}"
        return dictofroutes

    def authtoserver(self,adminusername,adminpassword):
        """
        Performs a POST request to the server login page to begin
        an administrative session, will login with admin credentials
        and retrieve a token, then assign that token to
        >>> APISession.authtoken
        """
        #apisession = APISession()
        # template for authentication packet
        authpayload = {
	        "name": str,
	        "password": str,
	        "_submit": "Submit",
            # I think the nonce can be anything?
            # try an empty one a few times with other fields fuzxzzed
	        "nonce": str #"84e85c763320742797291198b9d52cf6c82d89f120e2551eb7bf951d44663977"
        }
        ################################################################
        # Logging in as Admin!
        ################################################################
        # get the login form
        apiresponse = self.get(f"{self.ctfdurl}/login", allow_redirects=False)
        # if the server responds ok and its a setup, pre install
        if self.was_there_was_an_error(apiresponse.status_code):
            if apiresponse.status_code == 302 and apiresponse.headers["Location"].endswith("/setup"):
                errorlog(f"[-] CTFd installation has not been setup yet")
                raise Exception
                # the server was ok and responded with login
            else:
                # Grab the nonce
                authpayload['username'] = adminusername
                authpayload['password'] = adminpassword
                authpayload['nonce'] = apiresponse.text.split("csrfNonce': \"")[1].split('"')[0]
        # make the api request to the login page
        # this logs us in as admin
        apiresponse = self.post(
            url=self._getroute("login"),
            data = authpayload,
            allow_redirects=False,
        )
        if self.was_there_was_an_error(apiresponse.status_code) or (not apiresponse.headers["Location"].endswith("/challenges")):
            errorlog('invalid login credentials')
            raise Exception
        # grab a token and assign to self
        self._gettoken()

    def _gettoken(self):
        """
        Interfaces with the admin panel to retrieve a token
        """
        # get settings page in admin panel
        apiresponse = self.get(self._getroute("settings"))
        nonce = apiresponse.text.split("csrfNonce': \"")[1].split('"')[0]
        apiresponse = self.post(
                            url     =self._getroute("token"),
                            json    ={},
                            headers ={"CSRF-Token": nonce}
                            )
        if self.was_there_was_an_error(apiresponse.status_code) or (not apiresponse.json()["success"]):
            errorlog("[-] Token generation failed")
            raise Exception

        #greenprint("[+] Writing ctfd auth configuration")
        self.authtoken = apiresponse.json()["data"]["value"]
        #with open(".ctfd-auth", "w") as filp:
        #    yaml.dump({"url": self.ctfdurl, "token": self.authtoken}, filp)

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
        super(APISession, self).__init__(*args, **kwargs)

    def _apiauth(self):
        """
        Set auth headers for post administrative login
        ?User creation must be done with admin login, not apiauth?
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