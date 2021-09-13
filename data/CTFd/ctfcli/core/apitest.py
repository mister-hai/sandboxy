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

    def _getidbyname(self, challengename):#apiresponse:requests.Response, challengename="test"):
        """
        get challenge ID from server response to prevent collisions
        """
        self.getchallengelist()
        # list of all challenges
        apidict = self.apiresponse.json()["data"]
        for challenge in apidict:
            if str(challenge.get('name')) == challengename:
                # print data to STDOUT
                print(f"NAME: {challenge.get('name')}")
                print(f"ID: {str(challenge.get('id'))}")
                return challenge.get('id')

    def login(self):
        ##############################################################
        ## Login
        ##############################################################
        # get login page
        self.apiresponse = self.get(url=self.loginurl, allow_redirects=False)
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
        nonce = self.apiresponse.text.split("csrfNonce': \"")[1].split('"')[0]
        print("============\nInitial Nonce: "+ nonce + "\n===============")
        self.authpayload['nonce'] = nonce
        # send POST to Login URL
        apiresponse = self.apisession.post(url=self.loginurl,data = self.authpayload)#,allow_redirects=False)
        # grab admin login nonce

    def gettoken(self):
        ##############################################################
        ## Get token
        ##############################################################
        nonce = self.apiresponse.text.split("csrfNonce': \"")[1].split('"')[0]
        print("============\nAdmin Nonce: "+ nonce + "\n===============")
        # set csrf token in headers
        self.apisession.headers.update({"CSRF-Token": nonce})
        # POST to settings URL to generate token
        self.apiresponse = self.apisession.get(url=self.settingsurl,json={})
        # POST to tokensurl to obtain Token
        self.apiresponse = self.apisession.post(url=self._getroute('token'),json={})
        # Place token into headers for sessions to interact with WRITE permissions
        

    def _setauth(self):
        """
        Sets authorization headers with token
        >>> self.apisession.headers.update({"Authorization": "Token {}".format(authtoken)})
        """
        self.authtoken = self.apiresponse.json()["data"]["value"]
        self.apisession.headers.update({"Authorization": "Token {}".format(self.authtoken)})
    
    def getchallengelist(self):
        """
        Gets a list of all synced challenges
        """
        # get list of challenges
        self.apiresponse = self.apisession.get(self._getroute('challenges',admin=True),json=True)
        return self.apiresponse
        #self._getidbyname(apiresponse, 'test')
        #emptychallengesresponse = {"success": 'true', "data": []}

    def createbasechallenge(self):
        """
        Creates the initial challenge entry, to be 
        updated with relevant additional information
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

ctfdconnection = CTFdAPI()
ctfdconnection.login()
