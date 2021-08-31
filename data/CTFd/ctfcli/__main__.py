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
from utils.gitrepo import SandboxyGitRepository
from utils.ctfdrepo import Category,SandboxyCTFdRepository
from utils.challenge import Challenge
from utils.utils import errorlogger
from utils.apicalls import APISession



#class CTFCLI():
class SandBoxyCTFdLinkage():
    '''
    Maps to the command
    host@server$> ctfcli
    Used to upload challenges from the data directory in project root
    And manage the ctfd instance

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
    def __init__(self, 
                    ctfdtoken,
                    ctfdurl,
                    configname = "ctfcli.ini", 
                    ):
        try:
            greenprint("[+] Instancing a SandboxyCTFdLinkage()")
            self.PROJECTROOT         = os.getenv("PROJECT_ROOT")
            self.CTFD_TOKEN          = ctfdtoken #os.getenv("CTFD_TOKEN")
            self.CTFD_URL            = ctfdurl #os.getenv("CTFD_URL")
            self.configname          = configname
            # name of the yaml file expected to have the challenge data in each subfolder
            self.basechallengeyaml   = "challenge.yml"
            # reflects the data subdirectory in the project root
            self.DATAROOT            =  os.path.join(self.PROJECTROOT,"data")
            # represents the ctfd data folder
            self.CTFDDATAROOT        = os.path.join(self.DATAROOT, "ctfd")
            # folder expected to contain challenges
            # categories in here
                # then individual challenges
            self.challengesfolder    = os.path.join(self.CTFDDATAROOT, "challenges")
            # filename for the full challenge index
            self.masterlistfile      = "challengelist.yml"
            self.masterlistlocation  = os.path.join(self.challengesfolder, self.masterlistfile)
            self.masterlist          = Yaml(self.masterlistlocation)
            # template challenges
            self.TEMPLATESDIR        = os.path.join(self.challengesfolder, "ctfcli", "templates")
            #config stuff
            self.SCRIPTDIR           = os.path.join(self.CTFDDATAROOT,".ctfcli")
            self.CONFIGDIR           = os.path.join(self.CTFDDATAROOT,".ctfcli")
            self.CONFIGFILE          = os.path.join(self.CONFIGDIR, self.configname)
            self.config              = Config(self.COPNFIGFILE)
            # store url and token in config
            self.config["apiaccess"] = {"url": self.CTFD_URL, "ctf_token": self.CTFD_TOKEN}
            self.config.write()

            ###############################################
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
            self.location = lambda currentdirectory,childorsibling: os.path.join(currentdirectory,childorsibling)
        except Exception:
            errorlogger("[-] SandBoxyCTFdLinkage.__init__ Failed")

    def init(self):
        '''
    Link to CTFd instance with token and URI

>>> host@server$> ctfcli --ctfdtoken <token> --ctfdurl <url> init

    - Creates a masterlist of challenges in the repository
    - Creates a git repository and adds all the files
    - links repository with CTFd instance via disposable token

    TODO: Add Oauth via discord
        '''
        # need an array to carry data around
        #the init function will do the thing and return the data
        cat_bag = SandboxyGitRepository.createprojectrepo()
        # now we make the master list by adding all the data from the challenges 
        # to the yaml file and then write to disk
        #for category in cat_bag:
            #self.masterlist.data = category
        self.masterlist = cat_bag
        # TODO: TIMESTAMPS AND IDS!!!
        self.masterlist.writemasteryaml(self.masterlistfile, filemode="a")
        # we do this last so we can add all the created files to the git repo        
        SandboxyCTFdRepository.createprojectrepo()


    def getcategories(self,print=True):
        '''
    Maps to the command
    host@server$> ctfcli getcategories
    
    Get the names of all Categories
    Supply "print=False" to return a variable instead of display to screen 
        '''
        categories = self.masterlist['categories']
        if print == True:
            greenprint("Categories: {}".format(categories))
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

    def populatechallengelist(self, categories:Category):
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
                self.challengelistbuffer = open(self.listofchallenges).read()
                self.challengelistyaml   = yaml.load(self.challengelistbuffer, Loader=yaml.FullLoader) 

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

        For git operations, use gitoperations or your preferred terminal workflow
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




