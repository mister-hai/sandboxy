import re
import git
import fire
import json
import requests
import yaml
import click
import os, sys
import importlib
import subprocess
import configparser
from pathlib import Path
from requests import Session
from urllib.parse import urljoin
from urllib.parse import urlparse
from cookiecutter.main import cookiecutter


from utils.utils import redprint,greenprint,yellowboldprint, CATEGORIES
from utils.utils import CHALLENGE_SPEC_DOCS, DEPLOY_HANDLERS, blank_challenge_spec
from utils.Yaml import Yaml, KubernetesYaml, Challengeyaml, Config
from utils.repo import SandboxyCTFdRepository
from utils.challenge import Challenge
from utils.utils import errorlogger
from utils.apicalls import APISession


###############################################################################
#  CTFCLI HANDLING CLASS
###############################################################################
class Category(): #folder
    '''
    use getattr(),setattr() to add/query Challenge Entries
    this is used for keeping track internally

    ChallengeCategory:
        represents a folder in the PROJECTDIRECTORY/data/CTFd/challenges/ dir
      ChallengeEntry:
        represents a challenge.yaml
        name: thing
    '''
    def __init__(self,category):
        self.name = category
    
    def updaterepository(self, challenge):
        '''
    Updates the repository with any new content added to the category given
    if it doesnt fit the spec, it will issue an error    
    Try not to let your repo get cluttered
        '''

    def synccategory(self):
        '''
    Updates all challenges in CTFd with the versions in the repository
    Operates on the entire category 
        '''
            #call 


#class CTFCLI():
class SandBoxyCTFdLinkage():
    '''
    Maps to the command
    host@server$> ctfcli
    Used to upload challenges from the data directory in project root

    parameters are as follows:

        projectroot: Absolute path to project directory
        ctfdurl:     Url of ctfd instance
        ctfdtoken:   Auth token as given by settings page in CTFd
        configname:  Name of the configfile to use

        / not yet/
        loadconfig:  Loads from alternate configuration file
            DEFAULT: True
            INFO:    if False, ignores repository config
        / not yet/
    '''
    def __init__(self, projectroot, 
                       ctfdurl, 
                       ctfdtoken, 
                       configname = "ctfcli.ini", 
                       #loadconfig=True,
                       challengelist="challengelist.yml",
                       challengefilename="challenge.yml"
                       ):
        try:
            greenprint("[+] Instancing a SandboxyCTFdLinkage()")
            self.PROJECTROOT         = projectroot
            self.CTFD_TOKEN          = ctfdtoken
            self.CTFD_URL            = ctfdurl
            self.configname          = configname
            # name of the yaml file expected to have the challenge data in each subfolder
            self.basechallengeyaml   = challengefilename
            # filename for the full challenge index
            self.listofchallenges    = challengelist
            # reflects the data subdirectory in the project root
            self.DATAROOT            =  os.path.join(self.PROJECTROOT,"/data/")
            # represents the ctfd data folder
            self.CTFDDATAROOT        = os.path.join(self.DATAROOT, "/ctfd/")
            # folder expected to contain challenges
            # categories in here
                # then individual challenges
            self.challengesfolder    = os.path.join(self.CTFDDATAROOT, "/challenges/")
            # template challenges
            self.TEMPLATESDIR        = os.path.join(self.challengesfolder, "/ctfcli", "/templates/")
            #config stuff
            self.SCRIPTDIR           = os.path.join(self.CTFDDATAROOT,"/.ctfcli/")
            self.CONFIGDIR           = os.path.join(self.CTFDDATAROOT,"/.ctfcli/")
            self.CONFIGFILE          = os.path.join(self.CONFIGDIR, self.configname)
            self.config              = Config(self.COPNFIGFILE)
            # filebuffer for challengelist.yaml
            self.challengelistbuffer = open(self.listofchallenges).read()
            self.challengelistyaml   = yaml.load(self.challengelistbuffer, Loader=yaml.FullLoader) 
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

    def init(self):
        '''
    Maps to the command
    host@server$> ctfcli --ctfdtoken <token> --ctfdurl <url> init
    
    Link to CTFd instance with token and URI
        - Creates a masterlist of challenges in the repository
        - Creates a git repository and adds all the files

        '''
        cat_bag = []
        #statefulness, now we have ourselves in a spot
        self.location = self.challengesfolder
        for challenge_category in CATEGORIES:
            cat_bag.append(Category(challenge_category))
        # itterate over folders in challenge directory
        for categoryfolder in cat_bag:
            # get new location
            location = os.path.join(location, categoryfolder)
            # if its a repository category folder
            if categoryfolder in CATEGORIES:
                #get subfolder names
                challengefolders = self.getsubdirs(location)
                for challengefolder in challengefolders:
                    location = os.path.join(location, challenge)
                    # get the data
                    challenge_subfolders = self.getsubdirs(location) 
                    # load the yml describing the challenge
                    self.loadchallengeyaml(categoryfolder,challenge)
                    
                    # generate challenge
                    newchallenge = Challenge(category = categoryfolder, 
                                         location = location,
                                         challengefile = challengefile
                                         )
                    #load challenge.yml
                    newchallenge.load_challenge()
                pass
        
        #create repo
        self.repository = git.Repo.init(path=self.repo)
        #add all files in challenge folder to local repository
        self.repository.index.add(".")
        self.repository.index.commit('Initial commit')
        self.repository.create_head('master')

        # create config file
        config = configparser.ConfigParser()
        config["config"] = {"url": self.CTFD_URL, "ctf_token": self.CTFD_TOKEN}
        config.write()

        #generate a list of categories
        cat_bag = []
        for challenge_category in CATEGORIES:
            #put the cats in the bag
            cat_bag.append(Category(challenge_category))
        
        # add the challenges in each category folder to the category class
        # while also writing them to masterlist
        for category in cat_bag:
            pass


    def getcategories(self,print=True):
        '''
    Maps to the command
    host@server$> ctfcli getcategories
    
    Get the names of all Categories
    Supply "print=False" to return a variable instead of display to screen 
        '''
        categories = self.getsubdirs(self.challengesfolder)
        if print == True:
            greenprint("Categories: " + ",  ".join(categories))
        else:
            return categories

    def getchallengesbycategory(self, category, printscr=True):
        '''
    Maps to the command
    host@server$> ctfcli getchallengesbycategory
    Lists challenges in repo by category        
    Supply "print=False" to return a variable instead of utf-8 
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
    Maps to the command
    host@server$> ctfcli populatechallengelist
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
            # TODO: write list of challenges to yaml with tags
                danglies

    def synccategory(self, category:str):
        '''
    Maps to the command
    host@server$> ctfcli synccategory <categoryname>

    Synchronize all challenges in the given category, this uploads 
    the challenge data to CTFd
        '''
        try:
            greenprint("[+] Syncing Category: {}". format(category))
            challenges = self.getchallengesbycategory(category)
            for challenge in challenges:
                greenprint(f"Syncing challenge: {challenge}")
                challenge.syncinstalled()
        except Exception:
            errorlogger("[-] Failure to sync category! {}".format(challenge))

    def load_installed_challenges(self, remote=False):
        '''
        Lists the challenges installed to the server
        Use 
        
            --remote=False 
        
        to check the LOCAL repository
        '''
        if remote == True:
            apicall = APISession.generate_session()
            return apicall.get("/api/v1/challenges?view=admin", json=True).json()["data"]
        elif remote == False:
            SandboxyCTFdRepository.listinstalledchallenges()

    def newfromtemplate(self, type=""):
        '''
        Creates a new CTFd Challenge from template

        If no repo is present, uploads the DEFAULT template to CTFd
        '''
        # if no repo is present, uploads a template
        if type == "":
            type = "default"
            cookiecutter(os.path.join(self.TEMPLATESDIR, type))
        else:
            cookiecutter(os.path.join(self.TEMPLATESDIR,type))


###############################################################################
## Menu
## Maps to the command
## host@server$> ctfcli --interactive
###############################################################################
class Menu():
    '''
    Shows a useful menu for the users to operate with on the commmand line
    '''
    def __init__(self):
        self.ctfcli = SandBoxyCTFdLinkage
    #def main(self):
    #   pass


if __name__ == "__main__":
    #menu = Menu()
    #menu.main()
    
    # Load CLI
    fire.Fire(Menu)
