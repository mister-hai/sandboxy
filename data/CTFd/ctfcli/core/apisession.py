import json,yaml
from requests import Session
from ctfcli.utils.utils import errorlogger, errorlog, greenprint
#from utils.apifunctions import APIFunctions


class APIHandler(Session):
    """
    Handler for the APISession() class
        Provides a wrapper for the API Functions
    

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
        self.APIPREFIX = "/api/v1/"
        self.routeslist = ["challenges","tags","topics","awards",
        "hints", "flags","submissions","scoreboard",
        "teams","users","statistics","files", "notifications",
        "configs", "pages", "unlocks", "tokens", "comments"]
        self.template = {"data": [
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

    def was_there_was_an_error(self, responsecode)-> bool:
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
    def _apiauth(self):
        """
        Set auth headers for post administrative login
        ?User creation must be done with admin login, not apiauth?
        """
        # auth to server
        self.headers.update({"Authorization": "Token {}".format(self.authtoken)})

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
                authpayload['name'] = adminusername
                authpayload['password'] = adminpassword
                authpayload['nonce'] = apiresponse.text.split("csrfNonce': \"")[1].split('"')[0]
        # make the api request to the login page
        # this logs us in as admin
        apiresponse = self.post(
            url=self._getroute("login"),
            data = authpayload
            )#,allow_redirects=False,)
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
        apiresponse = self.post(url=self._getroute("token"),json={},headers ={"CSRF-Token": nonce})
        if self.was_there_was_an_error(apiresponse.status_code) or (not apiresponse.json()["success"]):
            errorlog("[-] Token generation failed")
            raise Exception

        #greenprint("[+] Writing ctfd auth configuration")
        self.authtoken = apiresponse.json()["data"]["value"]
        #with open(".ctfd-auth", "w") as filp:
        #    yaml.dump({"url": self.ctfdurl, "token": self.authtoken}, filp)

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
        """
        if jsonpayload.get("requirements"):
            installed_challenges = load_installed_challenges()
            required_challenges = []
            for r in challenge["requirements"]:
                if type(r) == str:
                    for c in installed_challenges:
                        if c["name"] == r:
                            required_challenges.append(c["id"])
                elif type(r) == int:
                    required_challenges.append(r)

            required_challenges = list(set(required_challenges))
            data = {"requirements": {"prerequisites": required_challenges}}
            r = s.patch(f"/api/v1/challenges/{challenge_id}", json=data)
            r.raise_for_status()

    def processtags(self, data):
        '''
        Processes tags for the challenges
        '''
        if jsonpayload.get("tags") and "tags" not in ignore:
           for tag in challenge["tags"]:
            r = s.post(
                f"/api/v1/tags", json={"challenge_id": challenge_id, "value": tag}
                )
            r.raise_for_status()

    def deleteremotehints(self,challenge_id,data):
        """
        deletes all hints from ctfd
        HARD MODE: ON
        """

    def processhints(self, data):
        '''
        process hints for the challenge
        '''
        if jsonpayload.get("hints") and "hints" not in ignore:
            for hint in challenge["hints"]:
                if type(hint) == str:
                    data = {"content": hint, "cost": 0, "challenge_id": challenge_id}
                else:
                    data = {
                        "content": hint["content"],
                        "cost": hint["cost"],
                        "challenge_id": challenge_id,
                    }

                r = s.post(f"/api/v1/hints", json=data)
                r.raise_for_status()

    def processtopics(self, data):
        '''
        process hints for the challenge
        '''
        for topic in challenge["topics"]:
            apiresponse = self.post(
                f"/api/v1/topics",
                json={
                    "value": topic,
                    "type": "challenge",
                    "challenge_id": challenge_id,
                },
            )
            r.raise_for_status()
    def processflags(self, data):
        '''
        process hints for the challenge
        '''
        if jsonpayload.get("flags") and "flags" not in ignore:
            for flag in challenge["flags"]:
                if type(flag) == str:
                    data = {"content": flag, "type": "static", "challenge_id": challenge_id}
                    r = s.post(f"/api/v1/flags", json=data)
                    r.raise_for_status()
                elif type(flag) == dict:
                    flag["challenge"] = challenge_id
                    r = s.post(f"/api/v1/flags", json=flag)
                    r.raise_for_status()

    def uploadfiles(self,data):
        """
        uploads files to the ctfd server
        """
        if jsonpayload.get("files") and "files" not in ignore:
            files = []
            for f in challenge["files"]:
                file_path = Path(challenge.directory, f)
                if file_path.exists():
                    file_object = ("file", file_path.open(mode="rb"))
                    files.append(file_object)
                else:
                    click.secho(f"File {file_path} was not found", fg="red")
                    raise Exception(f"File {file_path} was not found")

            data = {"challenge_id": challenge_id, "type": "challenge"}
            # Specifically use data= here instead of json= to send multipart/form-data
            r = s.post(f"/api/v1/files", files=files, data=data)
            r.raise_for_status()

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
    
