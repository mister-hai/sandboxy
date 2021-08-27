import yaml
import os, sys
import importlib
import subprocess
import configparser
from pathlib import Path

import click
# REPL interface for the CLI
import fire

#original imports from ctfcli
from .cli.challenges import Challenge
from .cli.config import Config
from .cli.plugins import Plugins
from .cli.templates import Templates

# move to this file
#from .utils.plugins import get_plugin_dir

#imports from boilerplate
from .utils.printing import redprint,greenprint,yellowboldprint
from utils.printing import errorlogger

#class CTFCLI(object):
class SandBoxyCTFdLinkage():
    '''
    Uses ctfcli to upload challenges from the data directory in project root
    '''
    def __init__(self):
        try:
            greenprint("[+] Instancing a SandboxyCTFdLinkage()")
            # set by .env and start.sh
            # reflects the directory you have sandboxy in, default is ~/sandboxy
            self.PROJECTROOT         =  os.getenv("PROJECTROOT",default=None)
            # set by .env and start.sh
            # reflects the data subdirectory in the project root
            self.DATAROOT            = os.getenv("DATAROOT", default=None)
            # represents the ctfd data folder
            self.CTFDDATAROOT        = os.path.join(self.DATAROOT, "ctfd")
            # set by .env and start.sh
            # ctfd command line access variables
            self.CTFD_TOKEN          = os.getenv("CTFD_TOKEN", default=None)
            self.CTFD_URL            = os.getenv("CTFD_URL", default=None)

            # folder expected to contain challenges
            self.challengesfolder    = os.path.join(self.CTFDDATAROOT, "challenges")
            # template challenges
            self.TEMPLATESDIR = os.path.join(self.challengesfolder, "ctfcli", "templates")
            # name of the yaml file expected to have the challenge data in each subfolder
            self.basechallengeyaml   = "challenge.yml"
            # filename for the full challenge index
            self.listofchallenges    = "challengelist.yml"
            # filebuffer for challengelist.yaml
            self.challengelistbuffer = open(self.listofchallenges).read()
            self.challengelistyaml   = yaml.load(self.challengelistbuffer, Loader=yaml.FullLoader) 
            #######################################################################
            # PLUGINS
            #######################################################################
            #   These are the files in "cli" folder
            # /home/moop/sandboxy/data/ctfd/ctfcli/plugins
            self.PLUGINDIRECTORY = os.path.join(self.CTFDDATAROOT,"ctfcli", "cli")
            self.loadplugins()
            ####################################
            #lambdas, Still in __init__
            ####################################
            # returns subdirectories , without . files/dirs
            self.getsubdirs = lambda directory: [name for name in os.listdir(directory) if os.path.isdir(name) and not re.match(r'\..*', name)]
            # open with read operation
            self.challengeyamlbufferr = lambda category,challenge: open(os.path.join(category,challenge,self.basechallengeyaml),'r')
            # open with write operation
            self.challengeyamlbufferw = lambda category,challenge: open(os.path.join(category,challenge,self.basechallengeyaml),'r')
            #loads a challenge.yaml file into a buffer
            self.loadchallengeyaml =  lambda category,challenge: yaml.load(self.challengeyamlbufferr(category,challenge), Loader=yaml.FullLoader)
            self.writechallengeyaml =  lambda category,challenge: yaml.load(self.challengeyamlbufferw(category,challenge), Loader=yaml.FullLoader)
        except Exception:
            errorlogger("[-] SandBoxyCTFdLinkage.__init__ Failed")

    def loadplugins(self):
        '''
        Loads Plugins from cli directory
            files must end in .py and have simple, descriptive names
            settattr is being used, no funny business!
        '''
        #loads files from the /ctfcli/cli directory for use as
        # REPL interface objects
        greenprint("[+] Loading Plugins from {}".format(self.PLUGINDIRECTORY))
        # for each of the files in the plugin directory
        for replimport in sorted(os.listdir(self.PLUGINDIRECTORY)):
            # get an absolute path to the file
            filepath = os.path.join(self.PLUGINDIRECTORY, replimport)
            greenprint("Loading {}".format(replimport))
            #import that file
            importedmodule = importlib.import_module(filepath)
            # add specified modules into class
            setattr(self,replimport,importedmodule)

    def init(self):
        '''
        Link to CTFd instance with token and URI
        '''
        #if not self.CTFD_TOKEN or not self.CTFD_URL:
        #    errorlogger("[-] NO INPUT, something is wrong")
        #    exit(1)
        try:
            ctf_url = click.prompt("Please enter CTFd instance URL")
            ctf_token = click.prompt("Please enter CTFd Admin Access Token")
            if (
                click.confirm(f"Do you want to continue with {ctf_url} and {ctf_token}")
                is False
                ):
                click.echo("Aborted!")
                return

            # check if .ctf repo folder already exists
            if Path(".ctf").exists():
                click.secho(".ctf/ folder already exists. Aborting!", fg="red")
                return
            else:
                os.mkdir(".ctf")

            config = configparser.ConfigParser()
            config["config"] = {"url": ctf_url, "access_token": ctf_token}
            config["challenges"] = {}

            with open(".ctf/config", "a+") as f:
                config.write(f)

            subprocess.call(["git", "init"])

        except Exception:
            errorlogger("[-] INVALID INPUT: {} {}".format(self.CTFD_URL,self.CTFD_TOKEN))
            exit(1)

    def getcategories(self,print:bool):
        '''
        Get the names of all Categories
        Supply "print=True" to display to screen instead of return a variable
        '''
        categories = self.getsubdirs(self.challengesfolder)
        if print == True:
            greenprint("Categories: " + ",  ".join(categories))
        else:
            return categories
    
    def getchallengesbycategory(self, category, printscr:bool):
        '''
        Lists challenges in DB by category
            Use this after getting a list of categories
        '''
        challenges = []
        for category in self.get_categories():
            pathtocategory = os.path.join(self.challengesfolder, category)
            challengesbycategory = self.getsubdirs(pathtocategory)
            for challenge in challengesbycategory:
                challenges.append(challenge)
            if printscr == True:
                yellowboldprint("[+] Challenges in Category: {}".format(category))
                print(challenge)
            else:
                return challenges

    def populatechallengelist(self):
        '''
        Indexes 
            PROJECTROOT/data/CTFd/challenges/{category}/ 
        for challenges and adds them to the master list
        '''
        challengelist = []
        # itterate over all categories
        for category in self.get_categories():
            pathtocategory = os.path.join(self.challengesfolder, category)
            # itterate over challenge subdirs
            challengesbycategory = self.getsubdirs(pathtocategory)
            for challenge in challengesbycategory:
                #open the challenge.yaml file to get the name
                self.challengelistyaml
            #danglies

    def synccategory(self, category:str):
        '''
        Takes a category name

        Synchronize all challenges in the given category
        where each challenge is in it's own folder.
        '''
        try:
            greenprint("[+] Syncing Category: {}". format(category))
            challenges = self.getchallengesbycategory(category)
            for challenge in challenges:
                greenprint(f"Syncing challenge: {challenge}")
                os.system(f"ctf challenge sync '{challenge}'; ctf challenge install '{challenge}'")
        except Exception:
            errorlogger("[-] Failure, INPUT: {}".format(challenge))

    def syncchallenge(challenge:str):
        '''
        Adds a challenge
            Must be in its own folder, in a category that has been indexed
        '''
        greenprint(f"Syncing challenge: {challenge}")
        try:
            os.system(f"ctf challenge sync '{challenge}'; ctf challenge install '{challenge}'")
        except Exception:
            errorlogger("[-] Failure, INPUT: {}".format(challenge))


    def newfromtemplate(self, type=""):
        '''
        Creates a new CTFd Challenge Folder

        If no repo is present, uploads a template to CTFd
        '''
        # if no repo is present, uploads a template
        if type == "":
            type = "default"
            cookiecutter(os.path.join(self.TEMPLATESDIR, type))
        else:
            cookiecutter(os.path.join(self.TEMPLATESDIR,type))

class Menu():
    '''
    Shows a useful menu for the users to operate with on the commmand line
    '''
    def __init__(self):
        pass
    def main(self):
        pass


if __name__ == "__main__":
    menu = Menu()
    menu.main()
    # Load CLI
    fire.Fire(SandBoxyCTFdLinkage)
