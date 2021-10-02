import os,configparser
class Config(configparser.ConfigParser):
    def __init__(self):#, configpath:Path):
        return super().__init__(self)
    def _getallowedcategories(self):
        try:
            #self.allowedcategories = self['repo']['categories'].split(",")
            self.allowedcategories = self.get('repo','categories').split(",")
            return self.allowedcategories
        except Exception:
            print("[-] Failed to read Allowed Categories from Config file --- ")
            exit()
    def _readconfig(self, configpath):
        try:
            self.cfgfilepath = os.path.abspath(configpath)
            print(f"[+] Reading Config {configpath}")
            with open(self.cfgfilepath,'r') as cfgfile:
                print(cfgfile.readlines())
                self.read(cfgfile.readlines())
        except Exception:
            print("[-] FAILED: Reading Config --- ")

asdf = Config()
asdf._readconfig('config.cfg')
