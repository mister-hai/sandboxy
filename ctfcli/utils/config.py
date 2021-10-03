
import configparser
from pygments import highlight
from pygments.formatters import TerminalFormatter
from pygments.lexers import IniLexer, JsonLexer
import os
import json
from ctfcli.utils.utils import greenprint,errorlogger
import subprocess
from pathlib import Path

def setauth(function_to_authorize):
    """
    Decorator to allow for authentication to the CTFd server instance.

    Set to use command line arguments by default, but uses config=True
    for loading, config does not require URL of CTFd server

    Will optionally take a token, or username/password combination
    BOTH METHODS REQUIRE URL, the only method not requiring a url
    is  using --config=True and supplying a token or username/password
    in the config file along with a URL
    Args:
        config          (bool): If true, uses config file for values
                                if False, uses supplied parameters
        ctfdurl         (str):  URI for CTFd server
        ctfdtoken       (str):  Token provided by admin panel in ctfd
        adminpassword   (str):  admin pass
        adminusername   (str):  admin name
    """
    def genauth(self,
            config:bool=False,
            url:str=None,
            token:str=None,
            username:str=None,
            password:str=None
            ):
        try:
            # if they want to read information from the config file
            if config == True:
                Config._readauthconfig()
            elif config == False:
                # they have given a url/token
                if (url != None) and (token != None):
                    function_to_authorize(url=url ,token=token)
                # they have given a url/password/username
                if (password != None) and (username != None) and (url != None) :
                    #run function with auth
                    function_to_authorize(url=url,
                                          password=password,
                                          username=username
                                        )
            Config._setauthconfig()
        except Exception:
            errorlogger("[-] Error: Failed to set authentication information" )
    return genauth

class Config():#configparser.ConfigParser):
    '''
Config class
Maps to the command
host@server$> python ./ctfcli/ config <command>
    '''
    def __init__(self, configpath:Path):
        #parser = configparser.ConfigParser()
        # Preserve case in configparser
        #self.optionxform = str
        self.config = configparser.ConfigParser()
        self._readconfig(configpath)
        #super(self).__init__()

    def _getallowedcategories(self):
        """
        Reads allowed categories from config file
        use during reload when scanning for changes
        """
        try:
            self.allowedcategories = self.config.get('default','categories').split(",")
            #self.allowedcategories = self['default']['categories'].split(",")
            return self.allowedcategories
        except Exception:
            errorlogger("[-] Failed to read Allowed Categories from Config file --- ")
            exit()

    def _readconfig(self, configpath):
        """
        Reads from config and sets data to class attribute
        """
        #with open(self.cfgfilepath, 'r') as self.configfile:
            #config = open(self.cfgfilepath)
        try:
            self.cfgfilepath = os.path.abspath(configpath)
            greenprint(f"[+] Reading Config {configpath}")
            #with open(self.cfgfilepath) as cfgfile:
            self.config.read(filenames=self.cfgfilepath)
        except Exception:
            errorlogger("[-] FAILED: Reading Config --- ")

        #self.read(self.cfgfilepath)
        #self.configfile.close()

    def _writeconfig(self):
        """
        Writes data from self.config to self.configfilepath
        """
        #with open(self.cfgfilepath, 'w') as self.configfile:
            #config = open(self.cfgfilepath)
        self.write(self.cfgfilepath)
        #self.configfile.close()

    def _readauthconfig(self) -> dict:#, cfgfile:Path):
        #self.config.read(cfgfile)
        try:
            greenprint("[+] Setting authentication information from config file")
            authdict = {
                'username' : self.get('auth', 'username'),
                'password' : self.get('auth', 'password'),
                'token' : self.get('auth','token'),
                'url' : self.get('auth', 'url')
            }
            return authdict
            #self.config.close()
        except Exception:
            errorlogger("[-] Failed to set authentication information from config file:")

    def _setauthconfig(self, authdict):#, cfgfile:Path):
        """
        Sets auth information in config file
        If the containers are breached, this doesnt matter
        DO NOT RECYCLE PASSWORDS, PERIOD!
        """
        try:
            greenprint("[+] Storing Authentication information")
            #self.cfgfile = open(cfgfile, 'w')
            #self.config.add_section('auth')
            self.set('auth','username',authdict['username'])
            # yeah its plain text, the admin password should remain on the
            # server , in the project folder, if you choose to use one
            # these passwords are RELAYED and should be 
            # considered as temporary as tokens
            self.set('auth','password', authdict['password'])
            self.set('auth','token', authdict["token"])
            self.set('auth','url', authdict['url'])
            self.close()
        except Exception:
            errorlogger("[-] Failed to store authentication information")

    def _storetoken(self, token):
        """
        Stores Access tokens from CTFd
        Only one at a time though. You should rotate them per access, also

        Args:
            token  (str): The token you have been provided
        """
        try:
            greenprint("[+] Storing Authentication information")
            #self.cfgfile = open(cfgfile, 'w')
            #self.config.add_section('auth')
            self.token = token
            self.set('auth','token',self.token)
        except Exception:
            errorlogger("[-] Failed to store authentication information")

    def edit(self, filepath:str=None,editor="micro"):
        '''
        >>> config edit
            Edit config with $EDITOR
        '''
        # set environment variables for editor
        #editor = os.getenv("EDITOR", editor)
        if filepath == None:
            command = f"{editor} {self.cfgfilepath}"
            subprocess.call(command)

    def path(self):
        '''
        ctfcli config path
            Show config path
        '''
        print("[+] Config located at {}".format(self.configpath))
    
    def loadalternativeconfig(self, configpath:str):
        '''
        Loads an alternative configuration
        ctfcli config loadalternativeconfig <configpath>
        '''
        #path = self.configpath
        #parser = configparser.ConfigParser()
        # Preserve case in configparser
        #parser.optionxform = str
        self.optionxform = str
        #parser.read(Path(configpath))
        self.read(Path(configpath))
        return self

    def previewconfig(self, as_string=False):
        '''
        Shows current configuration
        ctfcli config previewconfig
        '''
        config = super().__init__(self.configpath)
        d = {}
        for section in config.sections():
            d[section] = {}
            for k, v in config.items(section):
                d[section][k] = v
        preview = json.dumps(d, sort_keys=True, indent=4)
        if as_string is True:
            return preview
        else:
            print(preview)
    
    def view(self, color=True, json=False):
        
        '''
        view the config
        ctfcli config view
        '''
        with open(self.configpath) as f:
            if json is True:
                config = self.previewconfig(as_string=True)
                if color:
                    config = highlight(config, JsonLexer(), TerminalFormatter())
            else:
                config = f.read()
                if color:
                    config = highlight(config, IniLexer(), TerminalFormatter())
            print(config)
