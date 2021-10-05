from logging import debug
import requests
from pathlib import Path
from ctfcli.utils.config import Config
from ctfcli.utils.utils import errorlog, greenprint, errorlogger,yellowboldprint
from ctfcli.core.apitemplates import hintstemplate,topictemplate, flagstemplate
from ctfcli.utils.utils import redprint,DEBUG
from ctfcli.utils.utils import debugblue,debuggreen,debugred,debugyellow


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
            url:str=None,
            token:str=None,
            APIPREFIX:str="/api/v1/"
            ):
        #https://server.host.net/ctfd/
        self.url = url.replace('http://','').replace('https://','')
        self.token = token
        self.settingsurl = self.url + "/settings"
        self.APIPREFIX = APIPREFIX
        self.routeslist = ["challenges","tags","topics","awards",
        "hints", "flags","submissions","scoreboard","settings",
        "teams","users","statistics","files", "notifications",
        "configs", "pages", "unlocks", "tokens", "comments","login"]
        self.authpayload = {
            "name": str,
            "password": str,
            "_submit": "Submit",
            "nonce": str
            }
        self.synchedchallengelist:dict = None
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
        debuggreen("[DEBUG] Setting Headers to STEALTH MODE!")
        self.headers.update(headers)
        debugblue(f"[DEBUG] {self.headers}")

    def _settoken(self,token):
        """
        Sets the Authorization field in the headers with a token
        also sets self.token
        """
        debuggreen(f"[DEBUG] Setting Token for auth")
        debuggreen(f"[DEBUG] {token}")
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
            self.token = authdict.get('token')
            debuggreen(f"[DEBUG] New Header section")
            debugblue(f"[DEBUG] Authorization : Token {self.token}")
            self.headers.update({"Authorization": f"Token {self.token}"})
        # everything else
        debugblue(f"[DEBUG] contents of Authdict : {authdict}")
        for key in authdict:
            setattr(self,key,authdict.get(key))

    def _obtainauthtoken(self):
        """
        Secondary code flow to obtain authentication
        Can only be used post setup
        """
        debuggreen("[DEBUG] Attempting to obtain auth token via login")
        self._obtainauthtoken(self.username,self.password)
        #return self.gettoken()

    def _geturi(self, tag, admin=False, schema='http'):
        """
        returns a non api uri for browser emulation
        """
        try:
            #dictofroutes = {}
            if tag in self.routeslist:
                #dictofroutes[tag] = f"{self.ctfdurl}{self.APIPREFIX}{tag}"
                self.schema = schema
                self.route = f"{schema}://{self.url}/{tag}"
                if admin == True:
                    debuggreen(f"[DEBUG] Route {self.route}?view=admin")
                    self.route = f"{self.route}?view=admin"
                    return f"{self.route}"
                else:
                    debugyellow(f"[INFOR] Route {self.route}")
                    return f"{self.route}" #dictofroutes
        except Exception:
            errorlogger("[-] Route not found in accepted list")
            exit()

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
                self.route = f"{schema}://{self.url}{self.APIPREFIX}{tag}"
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


    def authtoserver(self,username:str=None,password:str=None):
        """
        GETS TOKEN FROM PASSWORD
        SECONDARY FLOW
        
        Performs a POST request to the server login page to begin
        an administrative session, will login with admin credentials
        and retrieve a token, then assign that token to

        >>> APISession.token
        
        This function is SUPPOSED to ignore tokens in the config

        I need to modify CTFd to work more better when APIscream

        Args:
            username    (str): username as string
            password    (str): password as string
        """
        debuggreen("[DEBUG] Start of APISession.authtoserver()")
        #apisession = APISession()
        # template for authentication packet
        # these should be set already if _setauth was used
        if username == None and password == None:
            try:
                name = getattr(self,"username")
                passw = getattr(self,"password")
            #if self.password == None or self.username == None:
            except:
            #    try:
            #        token = getattr(self,"token")
            #    except:
                debugred("[DEBUG] APISession.authtoserver() missing critical auth information")
                raise Exception
        else:
            name = username
            passw = password

        self.authtemplate = {
	        "name": name,
	        "password": passw,
	        "_submit": "Submit",
	        "nonce": str #"84e85c763320742797291198b9d52cf6c82d89f120e2551eb7bf951d44663977"
        }
        ################################################################
        # Logging in as Admin!
        ################################################################
        # get the login form
        self.loginurl = self._geturi('login')
        debuggreen(f"[DEBUG] Attempting to login to {self.loginurl} ")
        self.apiresponse = self.get(self._geturi('login'), allow_redirects=False)
        debugblue(f"[DEBUG] API RESPONSE : {self.apiresponse.status_code}")
        # if it is not a 200 OK and its a setup, pre install path
        # the server was ok and responded with login
        if self.apiresponse.status_code == 200:
            # Grab the nonce
            self.nonce = self.apiresponse.text.split("csrfNonce': \"")[1].split('"')[0]
            debuggreen(f"[DEBUG] Initial Nonce: {self.nonce}")
            self.authtemplate['nonce'] = self.nonce
        elif self._there_was_an_error(self.apiresponse.status_code):
            if self.apiresponse.status_code == 302 and self.apiresponse.headers["Location"].endswith("/setup"):
                errorlog(f"[-] CTFd installation has not been setup yet")
                raise Exception
        # make the api request to the login page
        # this logs us in as admin
        debuggreen(f"[DEBUG] sending POST to Login URL {self.authpayload}")
        self.apiresponse = self.post(
            url=self._geturi("login"),
            data = self.authtemplate
            )#,allow_redirects=False,)
        debugblue(f"[DEBUG] API RESPONSE : {self.apiresponse.status_code}")
        if self._there_was_an_error( self.apiresponse.status_code):# or (not self.apiresponse.headers["Location"].endswith("/challenges")):
            errorlogger('[-] invalid login credentials')
            raise Exception
        # grab a token
        return self._gettoken()
        # now look down!
    # this gets called next, so its declared after to keep track
    def _gettoken(self):
        """
        SECOND FLOW
        Interfaces with the admin panel to retrieve a token
        """
        # get settings page in admin panel
        self.apiresponse = self.get(self._geturi("settings",admin=True))
        debugblue(f"[DEBUG] API RESPONSE : {self.apiresponse.status_code}")
        self.nonce = self.apiresponse.text.split("csrfNonce': \"")[1].split('"')[0]
        debugblue(f"[DEBUG] Admin Nonce: {self.nonce}")
        # set csrf token in headers
        debuggreen(f"[DEBUG] Setting headers with admin nonce")
        self.headers.update({"CSRF-Token":self.nonce})
        debugblue(f"[DEBUG] request headers:")
        debugblue(f"[DEBUG] {self.headers}")
        debuggreen(f"[DEBUG] Requesting Token from Admin Panel")
        self.apiresponse = self.post(url=self._getroute("tokens",admin=True),json={},headers ={"CSRF-Token": self.nonce})
        debugblue(f"[DEBUG] API RESPONSE : {self.apiresponse.status_code}")
        if self._there_was_an_error (self.apiresponse.status_code) or (not self.apiresponse.json()["success"]):
            errorlogger("[-] Token generation failed")
            raise Exception
        self.token = self.apiresponse.json()["data"]["value"]
        debugblue(f"[DEBUG] API STATUS  : {self.apiresponse.status_code}")
        debugblue(f"[DEBUG] API RESPONSE: {self.apiresponse.json()}")
        
    def login(self, username:str=None, password:str=None):
        """
        Login
        used during a session
        STEP 1
        """
        # get login page
        self.loginurl = self._geturi('login')
        debuggreen(f"[DEBUG] Attempting to login to {self.loginurl} ")
        self.apiresponse = self.get(url=self.loginurl, allow_redirects=True)
        debugblue(f"[DEBUG] API RESPONSE : {self.apiresponse.status_code}")
        # set auth fields
        self.authpayload['name'] = username
        self.authpayload['password'] = password
        # set initial interaction nonce
        self.nonce = self.apiresponse.text.split("csrfNonce': \"")[1].split('"')[0]
        debuggreen(f"[DEBUG] Initial Nonce: {self.nonce}")
        self.authpayload['nonce'] = self.nonce
        # send POST to Login URL
        debuggreen(f"[DEBUG] sending POST to Login URL {self.authpayload}")
        self.apiresponse = self.post(url=self._getroute('login'),data = self.authpayload)#,allow_redirects=False)
        debugblue(f"[DEBUG] API RESPONSE : {self.apiresponse.status_code}")
        # now look down!
    # this gets called next, so its declared after to keep track
    def gettoken(self):
        """
        Get token
        used during a session
        STEP 2
        """
        # grab admin login nonce
        self.nonce = self.apiresponse.text.split("csrfNonce': \"")[1].split('"')[0]
        debugblue(f"[DEBUG] Admin Nonce: {self.nonce}")
        # set csrf token in headers
        debuggreen(f"[DEBUG] Setting headers with admin nonce")
        self.headers.update({"CSRF-Token":self.nonce})
        debugblue(f"[DEBUG] request headers:")
        debugblue(f"[DEBUG] {self.headers}")

        # POST to settings URL to generate token
        debuggreen(f"[DEBUG] POST to settings URL to generate token")
        self.apiresponse = self.get(url=self.settingsurl,json={})
        debugblue(f"[DEBUG] API RESPONSE : {self.apiresponse.status_code}")        
        # POST to tokensurl to obtain Token
        debuggreen(f"[DEBUG] POST to tokensurl to obtain Token")
        self.apiresponse = self.post(url=self._getroute('tokens'),json={})
        debugblue(f"[DEBUG] API STATUS  : {self.apiresponse.status_code}")
        debugblue(f"[DEBUG] API RESPONSE: {self.apiresponse.json()}")
        # Place token into headers for sessions to interact with WRITE permissions
        self.token = self.apiresponse.json()["data"]["value"]
        return self.token

    def _there_was_an_error(self, responsecode)-> bool:
        """ Returns False if no error"""
        # server side error]
        set1 = [404,504,503,500]
        set2 = [400,405,501]
        set3 = [500]
        if responsecode in set1 :
            errorlogger(f"[-] Server side error - No Resource Available in REST response - Error Code {responsecode}")
            debugblue(f"[DEBUG] Server side error - No Resource Available in REST response - Error Code {responsecode}")
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

    def _getchallengebyname(self,name) -> dict:
        """
        checks for existance of challenge by searching for name in 
        the list of all challenges returned by server
        and returns the ID
        """
        greenprint("[+] Looking for existing challenge with same parameters")
        if self.synchedchallengelist == None:
            self.getsyncedchallenges()
        
        challengelist = self.synchedchallengelist
        if len(challengelist) > 0:
            #self.listofnames = [name.get('name) for name in self.listofchallenges]
            for challenge in challengelist:
                challengename = challenge.get('name')
                if name == challengename:
                    return challenge
        elif len(self.listofchallenges) == 0:
            yellowboldprint("[!] No challenges are installed currently!")
            return None
        else:
            raise Exception

    def getsyncedchallenges(self):
        """
        Gets a json container of all the challenges synced to the server
        This is step one for any procedure modifying challenges
        We cant discern if a challenges attributes have been modified on the
        server by an administrator or a hacker
        
        Returns:
            synchedchallengelist    (dict): list of all challenges installed in server
        """
        debuggreen("[DEBUG] getting list of all challenges")
        endpoint = self._getroute('challenges',admin=True)
        self._setheaders()
        challengedata = self.get(url = endpoint, json=True)
        self.synchedchallengelist = challengedata.json()['data']
        debuggreen(f"[DEBUG] {self.synchedchallengelist}")
        return self.synchedchallengelist

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
        challengebyname = self._getchallengebyname(jsonpayload.get('name'))
        # challenge with that name exists already
        if challengebyname != None:
            yellowboldprint(f"[!] Challenge NAME : {challengebyname.get('name')}")
            yellowboldprint(f"[!] Exists under ID: {str(challengebyname.get('id'))}")
            yellowboldprint("[!] Skipping!")
            raise Exception("Challenge Exists")
        # challenge does not exist by that name on the server
        elif challengebyname == None:
            # create new challenge
            self._settoken(self.token)
            self.apiresponse = self.post(url=self._getroute('challenges', admin=True), 
                                                    json=jsonpayload,
                                                    allow_redirects=True)

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
        self.apiresponse = self.patch(self._getroute('challenges') + str(challenge_id), json=data)
        self.apiresponse.raise_for_status()

    def _processtags(self, challenge_id:int, jsonpayload:dict) -> requests.Response:
        '''
        Processes tags for the challenges
        '''
        #if jsonpayload.get("tags"):
        for tag in jsonpayload.get("tags"):
            self.apiresponse = self.post(
                    self._getroute('tags'), 
                    json={
                        "challenge_id": challenge_id,
                        "value": tag
                        }
                    )
            self.apiresponse.raise_for_status()

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
            data = file.open(mode="rb")
            files = {"file": data}

            # set headers for file upload
            self._settoken(self.token)
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