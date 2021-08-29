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
            # reflects the data subdirectory in the project root
            self.DATAROOT            =  os.path.join(self.PROJECTROOT,"data")
            # represents the ctfd data folder
            self.CTFDDATAROOT        = os.path.join(self.DATAROOT, "ctfd")
            # folder expected to contain challenges
            # categories in here
                # then individual challenges
            self.challengesfolder    = os.path.join(self.CTFDDATAROOT, "challenges")
            # filename for the full challenge index
            self.challengelist       = challengelist
            self.masterlistlocation  = os.path.join(self.challengesfolder, self.challengelist)
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
    Maps to the command
    host@server$> ctfcli --ctfdtoken <token> --ctfdurl <url> init
    
    Link to CTFd instance with token and URI
        - Creates a masterlist of challenges in the repository
        - Creates a git repository and adds all the files

        '''
        # need an array to carry data around
        cat_bag = []
        # make a new category for every category allowed
        for challenge_category in CATEGORIES:
            cat_bag.append(Category(challenge_category))
        # get list of all folders in challenges repo
        categoryfolders = self.getsubdirs(self.challengesfolder)
        # itterate over folders in challenge directory
        for category in categoryfolders:
            # if its a repository category folder
            if category in CATEGORIES:
                # add a new category to the bag of cats
                # dont forget to stick your head in and ROTATE >:3
                self.config['categories']
                cat_bag.append(Category(challenge_category))
                # track location change to subdir
                pwd = self.location(self.challengesfolder, category)
                #get subfolder names in category directory, wreprweswenting indivwidual chwallenges yippyippyippyipp
                challenges = self.getsubdirs(pwd)
                # itterate over the individual challenges
                for challengefolder in challenges:
                    # track location change to individual challenge subdir
                    pwd = self.location(challenges, challengefolder)
                    # list files and folders
                    challengefolderdata = os.listdir(pwd)
                    # itterate over them
                    for challengedata in challengefolderdata:
                        # set location to challenge subfolder
                        challengelocation = self.location(pwd, challengefolder)
                        # get solutions path
                        if challengedata == "solution":
                            solution = os.path.join(pwd, challengedata)
                        # get handouts path
                        if challengedata == "handout":
                            handout = os.path.join(pwd, challengedata)
                        # get challenge file 
                        # self.basechallengeyaml == "challenge.yml"
                        if challengedata == self.basechallengeyaml:
                            # get path to challenge file
                            challengefile  = os.path.join(pwd, challengedata)
                            # load the yml describing the challenge
                            #challengeyaml = Yaml(challengefile)
                            challengeyaml = Challengeyaml(challengefile)
                            # get the name of the challenge
                        # for challenges with a server side component
                        #if challenge_data == "serverside":
                        # files for the server to host for safer challenges 
                        #    challengesrc = os.path.join(pwd, challenge_data)
                        #if challenge_data == "deployment":
                        # kubernetes deployment with nsjail
                        #    deployment = os.path.join(pwd, challenge_data)

                # generate challenge for that category
                newchallenge = Challenge(
                        name = challengeyaml.name,
                        category = challengeyaml.category,
                        location = challengeyaml.challengelocation, 
                        challengefile = challengeyaml,
                        #challengesrc= challengeyaml.challengesrc,
                        #deployment = challengeyaml.deployment,
                        handout= handout,
                        solution= solution
                        )
                
                #add the new challenge to the category as 
                # its own named child
                setattr(cat_bag[category],challengeyaml['name'],newchallenge)

        SandboxyCTFdRepository.createprojectrepo()

        # itterate over category classes containing challenge children
        for category in cat_bag:

            self.masterlist[]


    def getcategories(self,print=True):
        '''
    Maps to the command
    host@server$> ctfcli getcategories
    
    Get the names of all Categories
    Supply "print=False" to return a variable instead of display to screen 
        '''
        categories = self.masterlist['categories']
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
