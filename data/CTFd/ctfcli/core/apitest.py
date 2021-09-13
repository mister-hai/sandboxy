import requests
class CTFdAPI():
    def __init__(self):
        """
        API calls for ctfd
        """
        self.loginurl = "http://127.0.0.1:8000/login"
        self.settingsurl = "http://127.0.0.1:8000/settings#tokens"
        self.serverurl = "http://127.0.0.1:8000/"
        self.useragent = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:28.0) Gecko/20100101  Firefox/28.0'}
        self.APIPREFIX = "/api/v1/"
        self.routeslist = ["challenges","tags","topics","awards",
            "hints", "flags","submissions","scoreboard",
            "teams","users","statistics","files", "notifications",
            "configs", "pages", "unlocks", "tokens", "comments"]
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

    def _getroute(self,tag, admin=False):
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
                self.route = f"{self.APIPREFIX}{self.APIPREFIX}{tag}"
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
        self.apiresponse = self.apisession.get(url=self.loginurl, allow_redirects=False)
        # set auth fields
        self.authpayload = {
            "name": str,
            "password": str,
            "_submit": "Submit",
            "nonce": str
            }
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
        self.apiresponse = self.apisession.post(url=self._getroute('token'),json={})
        # Place token into headers for sessions to interact with WRITE permissions
        self.authtoken = self.apiresponse.json()["data"]["value"]

    def createbasechallenge(self):
        """
        Creates the initial challenge entry, to be 
        updated with relevant additional information
        used during a session
        STEP 3
        """
        ##############################################################
        # Challenge Creation
        ##############################################################
        # happens first
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
        # create new challenge
        self.apiresponse = self.apisession.post(url=self._getroute('challenges'), data=self.challengetemplate,allow_redirects=False)

    def addflags(self):
        """
        Adds Flags to the newly created challenge
        used during a session
        STEP 4
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

ctfdconnection = CTFdAPI()
ctfdconnection.login()
ctfdconnection.gettoken()
ctfdconnection.createbasechallenge()
ctfdconnection.addflags()