import requests
class CTFdAPI():
    def __init__(self):
        """
        API calls for ctfd
        """
        self.loginurl = "http://127.0.0.1:8000/login"
        self.settingsurl = "http://127.0.0.1:8000/settings#tokens"
        self.serverurl = "127.0.0.1:8000"
        self.useragent = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:28.0) Gecko/20100101  Firefox/28.0'}
        self.headers = {
            'Connection': 'keep-alive', 
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
                        AppleWebKit/537.36 (KHTML, like Gecko) \
                        Chrome/93.0.4577.63 Safari/537.36',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9'
        }

        self.APIPREFIX = "/api/v1/"
        self.routeslist = ["challenges","tags","topics","awards",
            "hints", "flags","submissions","scoreboard", 'token',
            "teams","users","statistics","files", "notifications",
            "configs", "pages", "unlocks", "tokens", "comments"]
        self.authpayload = {
            "name": str,
            "password": str,
            "_submit": "Submit",
            "nonce": str
            }
        self.challengetemplate = {
                "name": 'command line test',
                "category": 'test',
                "value": "500",
                ##seperate request"tags": 'commandlinetest',
                'description':"A test of uploading via API CLI",
                ##seperate request 'flags':r'''test{testflag}'''
                "state":"hidden",
                "type": 'standard',
        }

        ##############################################################
        ## Start session
        ##############################################################
        # start session
        self.apisession = requests.Session()
        self.apisession.headers.update(self.useragent)

    def _setauth(self):
        """
        Sets authorization headers with token
        used during a session
        >>> self.apisession.headers.update({"Authorization": "Token {}".format(authtoken)})
        """
        self.apisession.headers.update({"Authorization": "Token {}".format(self.authtoken)})

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
                    print(f"[+] Route {self.route}")
                    return f"{self.route}?view=admin"
                else:
                    print(f"[+] Route {self.route}?view=admin")
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
        self.apiresponse = self.apisession.get(self._getroute('challenges',admin=True),json=True)
        return self.apiresponse

    def _getidbyname(self, challengename):#apiresponse:requests.Response, challengename="test"):
        """
        get challenge ID from server response to prevent collisions
        used during a session
        """

        self._getchallengelist()
        # list of all challenges
        apidict = self.apiresponse.json()["data"]
        for challenge in apidict:
            if str(challenge.get('name')) == challengename:
                # print data to STDOUT
                print(f"NAME: {challenge.get('name')}")
                print(f"ID: {str(challenge.get('id'))}")
                return challenge.get('id')

    def _getchallengeroutebyname(self, challengename):
        """
        request to the challenge endpoint ID
        specified by challenge name. It's easier by name?
        
        """

    def makevisible(self,challengename):
        """
        GET
        Makes the challenge visible, by default it is created hidden I guess
        """
        self.state = {"state":"visible"}
        self.apiresponse = self.apisession.get(url=self._endpointbyname(challengename),data=self.state)

    def login(self):
        """
        ##############################################################
        ## Login
        # used during a session
        # STEP 1
        ##############################################################
        """
        # get login page
        self.apiresponse = self.apisession.get(url=self.loginurl, allow_redirects=True)
        # set auth fields
        self.authpayload['name'] = "root"
        self.authpayload['password'] ="password"
        # set initial interaction nonce
        self.nonce = self.apiresponse.text.split("csrfNonce': \"")[1].split('"')[0]
        print("============\nInitial Nonce: "+self.nonce + "\n===============")
        self.authpayload['nonce'] =self.nonce
        # send POST to Login URL
        self.apiresponse = self.apisession.post(url=self.loginurl,data = self.authpayload)#,allow_redirects=False)
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
        self.apisession.headers.update({"CSRF-Token":self.nonce})
        # POST to settings URL to generate token
        self.apiresponse = self.apisession.get(url=self.settingsurl,json={})
        # POST to tokensurl to obtain Token
        self.apiresponse = self.apisession.post(url=self._getroute('tokens'),json={})
        # Place token into headers for sessions to interact with WRITE permissions
        self.authtoken = self.apiresponse.json()["data"]["value"]

    def createbasechallenge(self):
        """
        Creates the initial challenge entry, to be 
        updated with relevant additional information
        used during a session
        STEP 3 overall
        step 1 in challenge creation
        POST /api/v1/challenges HTTP/1.1
        """
        ##############################################################
        # Challenge Creation
        ##############################################################
        # happens first
        # create new challenge
        self.apiresponse = self.apisession.post(url=self._getroute('challenges'), 
                                                data=self.challengetemplate,
                                                allow_redirects=True)
        # original code
        #r = s.post("/api/v1/challenges", json=data)
        self.apiresponse.raise_for_status()
        self.challenge_data = self.apiresponse.json()
        self.challenge_id = self.challenge_data["data"]["id"]

    def postflags(self):
        """
        Adds Flags to the newly created challenge
        used during a session
        STEP 4 in overall
        step 2 in challenge chain
        POST /api/v1/flags HTTP/1.1

        """
        # get challenge ID from name , why they cant build it all at once is beyond me
        self.newchallengeID = self._getidbyname(self.apiresponse, 'command line test')
        ##############################################################
        # Flag Creation
        ##############################################################
        # this is sent second
        flagstemplate = {
            "challenge_id":self.newchallengeID,
            "content":r'''test{testflag}''',
            "type":"static",
            "data":""
        }
        self.apiresponse = self.apisession.post(
                                url=self._getroute('flags'), 
                                data=self.challengetemplate,
                                allow_redirects=False
                                )
        self.apiresponse.raise_for_status()

    def patchchallengevisible(self):
        """
        Sets challenge to visible and returns server data on challenge entry
        step 3
        PATCH /api/v1/challenges/1 HTTP/1.1
            {"state":"visible"}

        returns 
        HTTP/1.1 200 OK
        new_challenge_id = apiresponse.json()["data"]["id"]
        """
        self.state = {"state":"visible"}
        self.apiresponse = self.apisession.patch(self._getroute('challenges'), data=self.state)
        self.apiresponse.raise_for_status()

    def postflags(self, challengeid, flags):
        """
        Post to flags endpoint
        """
        data = {"content": flags, "type": "static", "challenge_id": challengeid}
        r = self.apisession.post(url=self._getroute('flags'), json=data)

    def initialsync(self):
        self.login()
        self.gettoken()
        self.createbasechallenge()
        self.addflags()

ctfdconnection = CTFdAPI()


# returns 
# HTTP/1.1 200 OK
#new_challenge_id = apiresponse.json()["data"]["id"]
{
    "success": 'true',
    "data": {
        "id": 1, 
        "name": "test",
        "value": 500,
        "description": "test 1",
        "category": "test",
        "state": "visible",
        "max_attempts": 0,
        "type": "standard",
        "type_data": {
            "id": "standard",
            "name": "standard",
            "templates": {
                "create": "/plugins/challenges/assets/create.html", 
                "update": "/plugins/challenges/assets/update.html",
                "view": "/plugins/challenges/assets/view.html"
                }, 
            "scripts": {
                "create": "/plugins/challenges/assets/create.js", 
                "update": "/plugins/challenges/assets/update.js", 
                "view": "/plugins/challenges/assets/view.js"
                }
            }
        }
    }
#step 4
# GET /admin/challenges/1 HTTP/1.1
# GET /admin/challenges/1 HTTP/1.1
# GET /api/v1/flags/types HTTP/1.1
# GET /api/v1/challenges/1/tags HTTP/1.1
# GET /api/v1/challenges?view=admin HTTP/1.1
# GET /api/v1/challenges/1/requirements HTTP/1.1
# HTTP/1.1 200 OK
# {"success": true, "data": [{"data": "", "challenge": 1, "id": 1, "content": "test{thisisatest}", "challenge_id": 1, "type": "static"}]}

# step 5
# GET /api/v1/challenges/1/files HTTP/1.1
# GET /api/v1/challenges/1/hints HTTP/1.1
# HTTP/1.1 200 OK