import requests
from pathlib import Path

class APIHandler(requests.Session):
    """
    Handler for the APISession() class
        Provides a wrapper for the API Functions
        
        This is NOT designed with an asynchronous focus
        
        This IS stateful
            the class attributes will reflect the operation in progress. 
            Thread this operation if you need asynchronous functionality

        for sneaky peekers:
        useragent = 'Mozilla/5.0 (X11; Linux x86_64; rv:28.0) Gecko/20100101  Firefox/28.0'
    Args: 
        url (str): The URL of the Server instance you are haxxing
        token (str): an authentication Token
    """
    def __init__(self,
            url:str=None,
            token:str=None,
            APIPREFIX:str="/api/v1/"
            ):
        #https://server.host.net/ctfd/
        # this was for development, you comment this out for regular use
        self.url = url.replace('http://','').replace('https://','')
        self.token = token
        self.settingsurl = self.url + "/settings"
        self.APIPREFIX = APIPREFIX
        self.routeslist = ["list","of","endpoint","names"]
        self.authpayload = {
            "name": str,
            "password": str,
            "_submit": "Submit",
            "nonce": str
            }

        super().__init__()

    def _setheaders(self):
        """
        Sets the headers to allow for file uploads
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
                    print(f"[+] Route {self.route}?view=admin")
                    self.route = f"{self.route}?view=admin"
                    return f"{self.route}"
                else:
                    print(f"[+] Route {self.route}")
                    return f"{self.route}" #dictofroutes
        except Exception:
            print("[-] Route not found in accepted list")
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

        self.apiresponse = self.get(self._geturi('login'), allow_redirects=False)
        # set values for POST request
        self.authpayload['name'] = username
        self.authpayload['password'] = password

        # the server was ok and responded with login
        if self.apiresponse.status_code == 200:
            # Grab the nonce
            self.nonce = self.apiresponse.text.split("csrfNonce': \"")[1].split('"')[0]
            self.authtemplate['nonce'] = self.nonce
        elif self.was_there_was_an_error(self.apiresponse.status_code):
            raise Exception
        # make the api POST request to the login page
        # this logs us in as admin
        self.apiresponse = self.post(url=self._geturi("login"),data = self.authtemplate)#,allow_redirects=False,)
        # check for errors in server response
        if self.was_there_was_an_error( self.apiresponse.status_code):# or (not self.apiresponse.headers["Location"].endswith("/challenges")):
            print('invalid login credentials')
            raise Exception
        # grab a token
        return self._gettoken()

    def _gettoken(self):
        """
        Interfaces with the admin panel to retrieve a token
        """
        # get settings page in admin panel
        self.apiresponse = self.get(self._geturi("settings",admin=True))
        # get nonce for admin session from response
        self.nonce = self.apiresponse.text.split("csrfNonce': \"")[1].split('"')[0]
        # use nonce to obtain token from API
        self.apiresponse = self.post(url=self._getroute("tokens",admin=True),json={},headers ={"CSRF-Token": self.nonce})
        # check if the server accepted the request
        if self.there_was_an_error (self.apiresponse.status_code) or (not self.apiresponse.json()["success"]):
            print("[-] Token generation failed")
            raise Exception

        # assign the token to the class instance so it can be easily reused and shared
        # bewtween code objects, now you can call other methods and the token
        # can be given to the server.# the server this code was written for accepts the 
        # tokens via the HEADERS and the directive "Authorization: <token_value>"
        self.token = self.apiresponse.json()["data"]["value"]
        self._setauth(self.token)

    def getdata(self):
        """
        Gets a json container of all the information allowed to be sent
        out, by that endpoint, for a specific authorization level
        """
        endpoint = self._getroute('challenges',admin=True)
        return self.get(url = endpoint, json=True).json()["data"]

    def _uploadfiles(self, challenge_id:str=None,file:Path=None):
        """
        uploads files to the ctfd server
        Only the handout.tar.gz should be uploaded as of now

        Args:
            file (TarFile): The file to upload to accompany the challenge
        """
        try:
            print(f"[+] Uploading {file}")
            jsonpayload = {                 
                "challenge_id": challenge_id,
                "type": "challenge"
                }
            # buffer data and pack into json container
            data = file.open(mode="rb")
            files = {"file": data}

            # set headers for file upload
            self._settoken(self.token)
            # set headers for file uploading
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
            print(f"[-] Could not upload file: {e}")

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

        # these are probably a better way, these are the requests built in exception types
            #except requests.exceptions.HTTPError as errh:
            #    print(errh)
            #except requests.exceptions.ConnectionError as errc:
            #    print(errc)
            #except requests.exceptions.Timeout as errt:
            #    print(errt)
            #except requests.exceptions.RequestException as err:
            #    print(err)
