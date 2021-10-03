import os,configparser

class Config():#configparser.ConfigParser):
    def __init__(self, configpath:Path):
        self.config = configparser.ConfigParser()
        self._readconfig(configpath)
    def _getallowedcategories(self):
        try:
            self.allowedcategories = self.config.get('DEFAULT','categories').split(",")
            return self.allowedcategories
        except Exception:
            print("[-] Failed to read Allowed Categories from Config file --- ")
    def _readconfig(self, configpath):
        try:
            self.cfgfilepath = os.path.abspath(configpath)
            print(f"[+] Reading Config {configpath}")
            self.config.read(filenames=self.cfgfilepath)
        except Exception:
            print("[-] FAILED: Reading Config --- ")

asdf = Config()
asdf._readconfig('config.cfg')
