import requests
from pathlib import Path
from ctfcli.utils.utils import errorlog, greenprint, errorlogger
from ctfcli.core.apitemplates import hintstemplate,topictemplate, flagstemplate
class APIHandler(requests.Session):
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
    def __init__(self,
            ctfdurl:str=None,
            authtoken:str=None,
            loginurl = "http://127.0.0.1:8000/login",
            settingsurl = "http://127.0.0.1:8000/settings#tokens",
            serverurl = "127.0.0.1:8000",
            APIPREFIX = "/api/v1/"            
            ):
        #https://server.host.net/ctfd/
        self.ctfdurl = ctfdurl
        self.authtoken = authtoken
        self.loginurl = loginurl
        self.settingsurl = settingsurl
        self.serverurl = serverurl
        self.APIPREFIX = APIPREFIX
        self.routeslist = ["challenges","tags","topics","awards",
        "hints", "flags","submissions","scoreboard",
        "teams","users","statistics","files", "notifications",
        "configs", "pages", "unlocks", "tokens", "comments"]
        self.authpayload = {
            "name": str,
            "password": str,
            "_submit": "Submit",
            "nonce": str
            }

        super().__init__()

    def _setheaders(self):
        """
        Sets the headers to allow for file uploads?
        """
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
                                AppleWebKit/537.36 (KHTML, like Gecko) \
                                Chrome/93.0.4577.82 Safari/537.36',
                    #'Origin': 'http://127.0.0.1:8000',
                    #'Referer': 'http://127.0.0.1:8000/admin/challenges/11',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Accept-Language': 'en-US,en;q=0.9' 
                }
        self.headers.update(headers)

    def _setauth(self):
        """
        Sets authorization headers with token
        used during a session
        >>> self.apisession.headers.update({"Authorization": "Token {}".format(authtoken)})
        """
        self.headers.update({"Authorization": "Token {}".format(self.authtoken)})

    def _obtainauthtoken(self):
        """
        Secondary code flow to obtain authentication
        Can only be used post setup
        """
        self.login()
        self.gettoken()

    def _getroute(self,tag, admin=False, schema='http'):
        """
        Gets API route string for Requests Session
        Args:
            tag (str): Route to send JSON/web request to
            admin (bool): Add ?view=admin' to params
        """
        try:
            #dictofroutes = {}
            if tag in self.routeslist:
                #dictofroutes[tag] = f"{self.ctfdurl}{self.APIPREFIX}{tag}"
                self.schema = schema
                self.route = f"{schema}://{self.serverurl}{self.APIPREFIX}{tag}"
                if admin == True:
                    print(f"[+] Route {self.route}?view=admin")
                    self.route = f"{self.route}?view=admin"
                    return f"{self.route}"
                else:
                    print(f"[+] Route {self.route}")
                    return f"{self.route}" #dictofroutes
        except Exception:
            print("[-] Route not found in accepted list")
            exit()

    def _getchallengelist(self):
        """
        Gets a list of all synced challenges
        used during a session
        """
        # get list of challenges
        self.apiresponse = self.get(self._getroute('challenges',admin=True),json=True)
        return self.apiresponse

    def _getidbyname(self, challengename):#apiresponse:requests.Response, challengename="test"):
        """
        get challenge ID from server response to prevent collisions
        used during a session
        """

        self._getchallengelist()
        # list of all challenges
        apidict = self.apiresponse.json()["data"]
        #challengeids = [{k: v} for x in apidict for k, v in x.items()]
        for challenge in apidict:
            if str(challenge.get('name')) == challengename:
                # print data to STDOUT
                print(f"NAME: {challenge.get('name')}")
                print(f"ID: {str(challenge.get('id'))}")
                return challenge.get('id')

    def authtoserver(self,adminusername,adminpassword):
        """
        Performs a POST request to the server login page to begin
        an administrative session, will login with admin credentials
        and retrieve a token, then assign that token to
        >>> APISession.authtoken
        """
        #apisession = APISession()
        # template for authentication packet
        self.authtemplate = {
	        "name": str,
	        "password": str,
	        "_submit": "Submit",
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
                self.authtemplate['name'] = adminusername
                self.authtemplate['password'] = adminpassword
                self.authtemplate['nonce'] = apiresponse.text.split("csrfNonce': \"")[1].split('"')[0]
        # make the api request to the login page
        # this logs us in as admin
        apiresponse = self.post(
            url=self._getroute("login"),
            data = self.authtemplate
            )#,allow_redirects=False,)
        if self.was_there_was_an_error(apiresponse.status_code) or (not apiresponse.headers["Location"].endswith("/challenges")):
            errorlog('invalid login credentials')
            raise Exception
        # grab a token and assign to self
        self._gettoken()


    def login(self):
        """
        ##############################################################
        ## Login
        # used during a session
        # STEP 1
        ##############################################################
        """
        # get login page
        self.apiresponse = self.get(url=self.loginurl, allow_redirects=True)
        # set auth fields
        self.authpayload['name'] = "root"
        self.authpayload['password'] ="password"
        # set initial interaction nonce
        self.nonce = self.apiresponse.text.split("csrfNonce': \"")[1].split('"')[0]
        print("============\nInitial Nonce: "+self.nonce + "\n===============")
        self.authpayload['nonce'] =self.nonce
        # send POST to Login URL
        self.apiresponse = self.post(url=self.loginurl,data = self.authpayload)#,allow_redirects=False)
        # grab admin login nonce

    def gettoken(self):
        """
        ##############################################################
        ## Get token
        # used during a session
        # STEP 2
        ##############################################################
        """
        self.nonce = self.apiresponse.text.split("csrfNonce': \"")[1].split('"')[0]
        print(f"============\nAdmin Nonce: {self.nonce}\n===============")
        # set csrf token in headers
        self.headers.update({"CSRF-Token":self.nonce})
        # POST to settings URL to generate token
        self.apiresponse = self.get(url=self.settingsurl,json={})
        # POST to tokensurl to obtain Token
        self.apiresponse = self.post(url=self._getroute('tokens'),json={})
        # Place token into headers for sessions to interact with WRITE permissions
        self.authtoken = self.apiresponse.json()["data"]["value"]


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


    def deleteremotefiles(self,token):
        """
        deletes files from ctfd server
        """

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
        return self.get(url = endpoint, json=True).json()["data"]

    def _createbasechallenge(self,jsonpayload:dict):
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
        self.apiresponse = self.post(url=self._getroute('challenges'), 
                                                json=jsonpayload,
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
            self._processtags(self.challenge_id,jsonpayload)
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
        self.hintstempl = hintstemplate()
        for hint in hints:
            if type(hint) == str:
                self.hintstempl["content"] = hint
                self.hintstempl["cost"] = hintcost
                self.hintstempl["challenge_id"] = challengeid
            else:
                self.hintstempl["content"] = hint["content"]
                self.hintstempl["cost"] = hint["cost"]
                self.hintstempl["challenge_id"] = challengeid
            #make request with hints template
            self.apiresponse = self.post(self._getroute('hints'), json=self.hintstempl)
            self.apiresponse.raise_for_status()

    def _processtopics(self, jsonpayload:dict):
        '''
        process hints for the challenge
        '''
        self.topictempl = topictemplate()
        for topic in jsonpayload.get("topics"):
            self.topictempl['value'] = topic
            self.apiresponse = self.post(self._getroute("topics"),json=self.topictempl)
            self.apiresponse.raise_for_status()

    def _processflags(self, challengeid:int, jsonpayload:dict) -> requests.Response:
        '''
        process hints for the challenge
        '''
        self.flagstempl = flagstemplate()
        for flag in jsonpayload.get("flags"):
                if type(flag) == str:
                    self.flagstempl["content"] = flag
                    self.flagstempl["type"] = "static"
                    self.flagstempl["challenge"] = challengeid
                    self.apiresponse = self.post(
                                                self._getroute("flags"),
                                                json=dict(self.flagstempl),
                                                allow_redirects=True
                                                )
                                            
                    self.apiresponse.raise_for_status()
                elif type(flag) == dict:
                    self.flagstempl["challenge"] = challengeid
                    self.apiresponse = self.post(self._getroute("flags"), json=flag)
                    self.apiresponse.raise_for_status()

    def _uploadfiles(self, file:Path, challenge_id:str=None):
        """
        uploads files to the ctfd server
        Only the handout.tar.gz should be uploaded as of now

        Args:
            file (TarFile): The file to upload to accompany the challenge
        """
        try:
            greenprint(f"[+] Uploading {file}")
            jsonpayload = {
                "challenge_id": challenge_id if challenge_id is not None else self.challenge_id, 
                "type": "challenge"
                }
            # buffer data and pack into json container
            data = open(file.absolute(),"r",encoding="latin-1", closefd=True)
            files = {"file": data}

            # set headers for file upload
            self._setauth()
            self._setheaders()
            # Specifically use data= here instead of json= to send multipart/form-data
            # the data field sends json encoded strings describing what to do with the files
            # the files field is the binary blob (or blobs) we want to have uploaded
            self.apiresponse = self.post(url = self._getroute('files'), files=files, data=jsonpayload)
            self.apiresponse.raise_for_status()
        except Exception as e:
            errorlogger(f"[-] Could not upload file: {e}")

