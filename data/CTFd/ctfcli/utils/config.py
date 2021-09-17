
import configparser
from pygments import highlight
from pygments.formatters import TerminalFormatter
from pygments.lexers import IniLexer, JsonLexer
import os
import json

import subprocess
from pathlib import Path

class Config(configparser.ConfigParser()):
    '''
Config class
Maps to the command
host@server$> ctfcli config <command>
    '''
    def __init__(self, configpath:Path):
        self.configpath = configpath
        #parser = configparser.ConfigParser()
        # Preserve case in configparser
        self.optionxform = str
        self.read(self.configpath)
        super(self).__init__(configpath)

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
