import json
from pathlib import Path
import yaml,os,subprocess
from pygments import highlight
from utils.utils import greenprint, redprint, errorlogger
from pygments.formatters import TerminalFormatter
from pygments.lexers import IniLexer, JsonLexer
import configparser

class Yaml(): #filetype
    '''
    Represents a challange.yml
    Give Path to challenge.yml
    '''
    def __init__(self, filepath):
        #set the base values
        # kubernetes or ctfd
        self.type = str
        # sets name of Yaml() to name of file
        self.name = os.path.basename(filepath)
        #get path of file
        self.filepath = Path(filepath)
        #set working dir of file
        self.directory = self.filepath.parent
        #if its a kubernetes config
        if self.filepath.endswith(".yaml"):
            redprint("[!] File is .yaml! Presuming to be kubernetes config!")
            self.type = "kubernetes"
        elif self.filepath.endswith(".yml"):
            greenprint("[+] Challenge File presumed (.yml)")
        # finally, load the file    
        self.loadyaml(filepath)

    def loadyaml(self):
        try:
            #open the yml file
            with open(self.filepath) as f:
                filedata = yaml.safe_load(f.read())#, filepath=filepath)
                #assign data to self
                #previous
                #super().__init__(filedata)
                self.data = filedata
        except Exception:
            errorlogger("[-] ERROR: Could not load .yml file")
    
    def writeyaml(self):
        '''
        remember to assign data to the file with
>>> thing = Yaml(filepath)
>>> thing.data['key'] = value
OR... you can assign python objects
and store the contents of whole classes
>>> thing.data = Category()
>>> thing.writeyaml()
        '''
        try:
            #open the yml file pointed to by the load operation
            with open(self.filepath) as file:
                filedata = yaml.safe_dump(file)
        except Exception:
            errorlogger("[-] ERROR: Could not Write .yml file, check the logs!")

    def writemasteryaml(self,name:str, filemode="a"):
        '''Special function to write the master yaml for the ctfd side of the repository
        remember to assign data to the file with
>>> thing = Yaml(filepath)
>>> thing.data = Category()
>>> thing.writeyaml()

File mode is set to append by default so you can manually fix the repo list

        '''
        try:
            #open the yml file pointed to by the load operation
            with open(self.filepath, filemode) as file:
                filedata = yaml.safe_dump(file)
                file.write
        except Exception:
            errorlogger("[-] ERROR: Could not Write .yml file, check the logs!")

class KubernetesYaml(Yaml): #file
    '''
    Represents a Kubernetes specification
    future
    '''
    def __init__(self):
        pass

class Challengeyaml(): #file
    '''
    Represents the challenge.yml as exists in the folder for that specific challenge
    '''
    def __init__(self,yamlfile):
        #get a representation of the challenge.yaml file
        self.challengeyaml = Yaml(yamlfile)
        self.yamldata = self.challengeyaml.data
        # name of the challenge
        self.name        = self.challengeyaml['name']
        self.author      = self.challengeyaml['author']
        self.category    = self.challengeyaml['category']
        self.description = self.challengeyaml['description']
        self.value       = self.challengeyaml['value']
        self.type        = self.challengeyaml['type']


class Config():
    '''
Config class
Maps to the command
host@server$> ctfcli config <command>
    '''
    def __init__(self, configpath):
        self.configpath = configpath
        parser = configparser.ConfigParser()
        # Preserve case in configparser
        parser.optionxform = str
        parser.read(Path(self.configpath))
        return parser

    def edit(self, editor="micro"):
        '''
        ctfcli config edit
            Edit config with $EDITOR
        '''
        # set environment variables for editor
        editor = os.getenv("EDITOR", editor)
        command = editor, 
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
        parser = configparser.ConfigParser()
        # Preserve case in configparser
        parser.optionxform = str
        parser.read(Path(configpath))
        return parser

    def previewconfig(self, as_string=False):
        '''
        Shows current configuration
        ctfcli config previewconfig
        '''
        config = self.load_config(self.configpath)
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
        with open(self.configlocation) as f:
            if json is True:
                config = self.preview_config(as_string=True)
                if color:
                    config = highlight(config, JsonLexer(), TerminalFormatter())
            else:
                config = f.read()
                if color:
                    config = highlight(config, IniLexer(), TerminalFormatter())
            print(config)
