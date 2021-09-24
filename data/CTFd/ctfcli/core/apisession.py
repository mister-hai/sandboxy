import requests
from pathlib import Path
from ctfcli.utils.config import Config
from ctfcli.utils.utils import errorlog, greenprint, errorlogger,yellowboldprint
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
        token (str): The authentication Token given in the settings page of the admin panel on the CTFd server
    """
    def __init__(self,
            ctfdurl:str=None,
            token:str=None,
            loginurl:str=None,# = "http://127.0.0.1:8000/login",
            settingsurl:str=None,# = "http://127.0.0.1:8000/settings#tokens",
            serverurl:str=None,# = "127.0.0.1:8000",
            APIPREFIX:str=None# = "/api/v1/"            
            ):
        #https://server.host.net/ctfd/
        self.ctfdurl = ctfdurl
        self.token = token
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
                    #'Accept-Encoding': 'gzip, deflate, br',
                    'Content-Transfer-Encoding': 'application/gzip',
                    #'Accept-Language': 'en-US,en;q=0.9' 
                }
        self.headers.update(headers)

    def _settoken(self,token):
        """
        Sets the Authorization field in the headers with a token
        also sets self.token
        """
        self.headers.update({"Authorization": f"Token {token}"})
        self.token = token

    def _setauth(self,authdict:dict):
        """
        Sets authorization with token or username/password
        used during a session
        
        Args:
            authdict = {
                        'username' : str,
                        'password' : str,
                        'token' : str,
                        'url' : str
                        }
        """
        # if there is a token provided
        if authdict.get('token') != None:
            self.headers.update({"Authorization": f"Token {authdict.get('token')}"})
        # everything else
        for key in authdict:
            setattr(self,key,authdict.get(key))

    def _obtainauthtoken(self):
        """
        Secondary code flow to obtain authentication
        Can only be used post setup
        """
        self.login()
        return self.gettoken()

    def _getroute(self,tag, admin=False, schema='http'):
        """
        Gets API route string for Requests Session
        Args:
            tag (str): Route to send JSON/web request to
            admin (bool): view admin route
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


    def authtoserver(self,username,password):
        """
        GETS TOKEN FROM PASSWORD

        Performs a POST request to the server login page to begin
        an administrative session, will login with admin credentials
        and retrieve a token, then assign that token to
        >>> APISession.token
        """
        #apisession = APISession()
        # template for authentication packet
        self.authtemplate = {
	        "name": username,
	        "password": password,
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
        # grab a token
        return self._gettoken()


    def login(self, username:str=None, password:str=None):
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
        self.authpayload['name'] = username
        self.authpayload['password'] = password
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
        self.token = self.apiresponse.json()["data"]["value"]
        return self.token


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
        self.token = apiresponse.json()["data"]["value"]
        #with open(".ctfd-auth", "w") as filp:
        #    yaml.dump({"url": self.ctfdurl, "token": self.token}, filp)

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

    def _getchallengebyname(self,name):
        """
        checks for existance of challenge by searching for name in 
        the list of all challenges returned by server
        and returns the ID
        """
        greenprint("[+] Looking for existing challenge with same parameters")
        self.listofchallenges = self.getsyncedchallenges()
        self.listofnames = [name for name in self.listofchallenges.get('name')]
        if name in self.listofnames:
            #challenge_id = challenge.get('id')
            return self.listofchallenges.get('name')
        else:
            return None

    def getsyncedchallenges(self):
        """
        Gets a json container of all the challenges synced to the server
        This is step one for any procedure modifying challenges
        We cant discern if a challenges attributes have been modified on the
        server by an administrator or a hacker
        """
        endpoint = self._getroute('challenges',admin=True)
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

        #check for existing challenge
        challengebyname = self._getchallengebyname(jsonpayload.get['name'])
        # challenge with that name exists already
        if challengebyname != None:
            yellowboldprint(f"[!] Challenge NAME : {challengebyname.get('name')}")
            yellowboldprint(f"[!] Exists under ID: {str(challengebyname.get('id'))}")
            yellowboldprint("[!] Skipping!")
            raise Exception("Challenge Exists")
        # challenge does not exist by that name on the server
        elif challengebyname == None:
            # create new challenge
            self.apiresponse = self.post(url=self._getroute('challenges'), 
                                                    json=jsonpayload,
                                                    allow_redirects=True)
            # original code
            #r = s.post("/api/v1/challenges", json=data)
            self.apiresponse.raise_for_status()
            self.challenge_data = self.apiresponse.json()
            self.challenge_id = self.challenge_data["data"]["id"]
            greenprint(f"[+] Challenge ID: {self.challenge_id}")

            ##############################################################
            # Everything below happens AFTER the challenge is created
            ##############################################################

    def _process(self,tag:str,challenge_id , jsonpayload:dict):
        """
        Uploads/sets sattributes on challenge on server after initial creation
        of the challenge entry

        Some challenges may have more or less information to sync depending
        on the challenge creators intents and designs
        """
        # Create new flags
        if tag == 'flags':
            self._processflags(challenge_id,jsonpayload)
        # Update topics
        if tag == 'topics':
            self._processtopics(challenge_id,jsonpayload)
        # Update tag
        if tag == 'tags':
            self._processtags(challenge_id,jsonpayload)
        # Upload files
        if tag == 'files':
            self._uploadfiles(challenge_id,jsonpayload.get(tag))
        # Create hints
        if tag == 'hints':
            self._processhints(challenge_id,jsonpayload)
        # Update requirements
        if tag == 'requirements':
            self._processrequirements(challenge_id,jsonpayload)

    def _processrequirements(self, challenge_id:int, jsonpayload:dict) -> requests.Response:
        """
        Use a PATCH request to modify the Challenge Requirements
        This is done towards the end
        """
        required_challenges = []
        for requirements in jsonpayload.get("requirements"):
            # if the requirements are other challenges
            if type(requirements) == str:
                required_challenges.append(challenge_id)
            # if the requirement is a score value
            elif type(requirements) == int:
                required_challenges.append(requirements)
        required_challenges = list(set(required_challenges))
        data = {"requirements": {"prerequisites": required_challenges}}
        apiresponse = self.patch(self._getroute('challenges') + str(challenge_id), json=data)
        apiresponse.raise_for_status()

    def _processtags(self, challenge_id:int, jsonpayload:dict) -> requests.Response:
        '''
        Processes tags for the challenges
        '''
        #if jsonpayload.get("tags"):
        for tag in jsonpayload.get("tags"):
            apiresponse = self.post(
                    self._getroute('tags'), 
                    json={
                        "challenge_id": challenge_id,
                        "value": tag
                        }
                    )
            apiresponse.raise_for_status()

    def _processhints(self,challenge_id:int,hints):
        '''
        process hints for the challenge
        Hints are used to give players a way to buy or have suggestions. They are not
        required but can be nice.
        Can be removed if unused
        Accepts dictionaries or strings
        #    - {
        #        content: "This hint costs points",
        #        cost: 10
        #    }
        #    - This hint is free
        '''
        self.deletehintbyid(challenge_id)
        self.hintstempl = hintstemplate()
        # sent to server
        #{"challenge_id":int,"content": str,"cost": int}
        # returned from yaml load
        # [
        #   {
        #       'content': 'braille encoded text', 
        #       'cost': 100
        #   }, 
        # 'open with a stego tool!'
        # ]
        # if its only one hint and its free
        #if type(hints) == str:
        #    self.hintstempl["content"] = hints
        #    self.hintstempl["cost"] = 0
        #    self.hintstempl["challenge_id"] = challenge_id
        #    self.apiresponse = self.post(self._getroute('hints'), json=self.hintstempl)
        # if its one hint with a cost value
        #elif type(hints) == dict:
        #    self.hintstempl["content"] = hints["content"]
        #    self.hintstempl["cost"] = hints["cost"]
        #    self.hintstempl["challenge_id"] = challenge_id
        #    self.apiresponse = self.post(self._getroute('hints'), json=self.hintstempl)
        # if its multiple hints
        #elif type(hints) == list:
            # we process them like before but itteratively
        for each in hints:
                #if it has a cost value
                if type(each) == dict:
                    self.hintstempl["content"] = hints["content"]
                    self.hintstempl["cost"] = hints["cost"]
                    self.hintstempl["challenge_id"] = challenge_id
                    self.apiresponse = self.post(self._getroute('hints'), json=self.hintstempl)
                # if its free
                if type(hints) == str:
                    self.hintstempl["content"] = hints
                    self.hintstempl["cost"] = 0
                    self.hintstempl["challenge_id"] = challenge_id
                    self.apiresponse = self.post(self._getroute('hints'), json=self.hintstempl)
        #make request with hints template
        #self.apiresponse = self.post(self._getroute('hints'), json=self.hintstempl)
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

    def _processflags(self, challenge_id:int, jsonpayload:dict) -> requests.Response:
        '''
        process hints for the challenge
        '''
        self.flagstempl = flagstemplate()
        self.flagstempl["challenge"] = challenge_id
        flags = jsonpayload.get("flags")
        # there is only one flag, it should be a string
        # unless there is a 
        # flags:
        #   - flag{flagstring}
        # !?!?right?!?!
        # to extend to multiple flags, add to the challenge class input
        if (type(flags) == str): # and (len(flags) == 1):
                    self.flagstempl["content"] = flags
                    self.flagstempl["type"] = "static"
                    self.apiresponse = self.post(
                                                self._getroute("flags"),
                                                json=dict(self.flagstempl),
                                                allow_redirects=True
                                                )
                                            
                    self.apiresponse.raise_for_status()
        if type(flags) == dict:
            self.apiresponse = self.post(self._getroute("flags"), json=self.flagstempl)
            self.apiresponse.raise_for_status()

    def _uploadfiles(self, challenge_id:str=None,file:Path=None):
        """
        uploads files to the ctfd server
        Only the handout.tar.gz should be uploaded as of now

        Args:
            file (TarFile): The file to upload to accompany the challenge
        """
        try:
            greenprint(f"[+] Uploading {file}")
            jsonpayload = {                 # this was for a rando idea I had, might still be useful
                "challenge_id": challenge_id,# if challenge_id is not None else self.challenge_id, 
                "type": "challenge"
                }
            # buffer data and pack into json container
            data = file.open(mode="rb")#, closefd=True,encoding="cp1252",)
            files = {"file": data}

            # set headers for file upload
            self._setauth()
            self._setheaders()
            # Specifically use data= here instead of json= to send multipart/form-data
            # the data field sends json encoded strings describing what to do with the files
            # the files field is the binary blob (or blobs) we want to have uploaded
            self.apiresponse = self.post(url = self._getroute('files'), 
                                         files = files, 
                                         data = jsonpayload, 
                                         verify = False)
            self.apiresponse.raise_for_status()
        except Exception as e:
            errorlogger(f"[-] Could not upload file: {e}")

    def deletehintbyid(self, challenge_id):
        # Delete existing hints
        try:
            greenprint(f'[+] Deleting existing hints for challenge {challenge_id}')
            self.hintstempl = hintstemplate()
            data = {"challenge_id": challenge_id, "type": "challenge"}
            # request a list of all hints
            current_hints = self.get(self._getroute('hints'), json=data).json()["data"]
            for hint in current_hints:
                # get the hint for the indicated challenge
                if hint["challenge_id"] == challenge_id:
                    hint_id = hint["id"]
                    self.apiresponse = self.delete(self._getroute('hints')+ hint_id, json=True)
                    self.apiresponse.raise_for_status()
        except Exception:
            errorlogger(f"[-] ERROR: Could not delete hints for challenge ID: {challenge_id} ")