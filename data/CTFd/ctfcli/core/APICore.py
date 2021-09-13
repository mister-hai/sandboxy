# there are two sets of functions to perform the same operations
# one is procedural, the other is monolithic
# choose which to use , suiting your specific situation
from requests import Session
from ctfcli.utils.utils import errorlogger, errorlog
class APICore(Session):
    def __cls__(cls):
        cls.loginurl = "http://127.0.0.1:8000/login"
        cls.settingsurl = "http://127.0.0.1:8000/settings#tokens"
        cls.serverurl = "127.0.0.1:8000"
        cls.APIPREFIX = "/api/v1/"
        cls.routeslist = ["challenges","tags","topics","awards",
        "hints", "flags","submissions","scoreboard",
        "teams","users","statistics","files", "notifications",
        "configs", "pages", "unlocks", "tokens", "comments"]
        cls.authpayload = {
            "name": str,
            "password": str,
            "_submit": "Submit",
            "nonce": str
            }
        cls.challengetemplate = {
                "name": str,
                "category": str,
                "value": int,
                'description':str,
                "state":str,
                "type": str,
                #"tags": list,#[],
                #'flags':r'''test{testflag}'''
                #"solves": int,#4,
                #"solved_by_me": str,#'false',
                #"template": str,#"/plugins/multiple_choice/assets/view.html",
                #"script": str#"/plugins/multiple_choice/assets/view.js"
        }
        cls.topictemplate = {
                    "value": str,
                    "type": str,#"challenge",
                    "challenge_id": int,
                }
        cls.hintstemplate = {
                    "content": str,
                    "cost": int,
                    "challenge_id": int,
                }
        cls.flagstemplate = {
            "success": str,#'true',
            "data": [
                {
                    "content": str,#"test{thisisatest}",
                    "id": int,#1,
                    "challenge_id": int,#1,
                    "type": str,#"static",
                    "data": str,#"",
                    "challenge": int#1
                }
            ]
        }
        cls.tokentemplate = {
				"success": str,#'true', 
				"data": {
						"created": str,#"2021-09-12T08:59:52.421062+00:00", 
						"value": str,#"e2c1cb51859e5d7afad6c2cd82757277077a564166d360b48cafd5fcc1e4e015", 
						"type": str,#"user",
						"id": int,#1,
						"expiration":str,#"2021-10-12T08:59:52.421073+00:00",
						"user_id": int#1
						}
				}
        # template for authentication packet
        cls.authtemplate = {
	        "name": str,
	        "password": str,
	        "_submit": "Submit",
            # I think the nonce can be anything?
            # try an empty one a few times with other fields fuzxzzed
	        "nonce": str #"84e85c763320742797291198b9d52cf6c82d89f120e2551eb7bf951d44663977"
        }
    def _setauth(self):
        """
        Sets authorization headers with token
        used during a session
        >>> self.apisession.headers.update({"Authorization": "Token {}".format(authtoken)})
        """
        self.apisession.headers.update({"Authorization": "Token {}".format(self.authtoken)})

    def _obtainauthtoken(self):
        """
        Secondary code flow to obtain authentication
        Can only be used post setup
        """
        self.login()
        self.gettoken()
        #self.createbasechallenge()
        #self.addflags()

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

    def authtoserver(self,adminusername,adminpassword):
        """
        Performs a POST request to the server login page to begin
        an administrative session, will login with admin credentials
        and retrieve a token, then assign that token to
        >>> APISession.authtoken
        """
        #apisession = APISession()

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

