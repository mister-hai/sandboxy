import os
from pathlib import Path
from ctfcli.core.yamlstuff import Yaml
from ctfcli.core.category import Category
from ctfcli.core.challenge import Challenge
from ctfcli.core.repository import Repository
from ctfcli.core.masterlist import Masterlist
from ctfcli.core.apisession import APIHandler
from ctfcli.utils.lintchallenge import Linter
from ctfcli.utils.utils import getsubdirs,redprint
from ctfcli.utils.utils import errorlogger,yellowboldprint,greenprint,logger

###############################################################################
#
###############################################################################
class SandboxyCTFdRepository():
    """
    Backend to CTFd Repository
    """
    def __init__(self,
                repositoryfolder:Path ,
                masterlistlocation
                ):
        self.masterlistlocation = masterlistlocation
        self.repofolder = repositoryfolder
        self.allowedcategories = list
        try:
            greenprint("[+] Instancing a SandboxyCTFdRepository()")
            super(SandboxyCTFdRepository, self).__init__()
        except Exception as e:
            errorlogger(f"[-] FAILED: Instancing a SandboxyCTFdLinkage(){e}")

    def _createrepo(self, allowedcategories)-> Repository:
        '''
        Performs all the actions necessary to create a repository
        From the Challenges Folder in the DATAROOT

        Creates the masterlist and Repository objects

        Returns:
        Masterlist, Repo (Tuple): Two new data objects

        '''
        greenprint("[+] Starting Repository Scan")
        dictofcategories = {}
        #repocategoryfolders = os.listdir(os.path.abspath(self.repofolder))
        repocategoryfolders = getsubdirs(self.repofolder)
        #greenprint(f"[+] Categories: {[f'{folder}\n' for folder in repocategoryfolders]}")
        # itterate over folders in challenge directory
        for category in repocategoryfolders:
            categorypath = Path(os.path.join(self.repofolder, category))
            # if its a repository category folder in aproved list
            if category.stem in allowedcategories:
                # process the challenges in that category
                newcategory = self._processcategory(categorypath)
                # this dict contains the entire repository now
                dictofcategories[newcategory.name] = newcategory
        # assign all categories to repository class
        # using protoclass + dict expansion
        newrepo = Repository(**dictofcategories)
        # return this class to the upper level scope
        return newrepo

    def _addmasterlist(self, masterlist:Masterlist):
        '''
        Adds a masterlist file to self
        '''
        setattr(self,'masterlist',masterlist)

    def _processcategory(self,categorypath:Path)-> Category:
        '''
        Itterates over a Category folder to add challenges to the database
        '''
        greenprint(f"[+] Found Category {categorypath.name}")
        #create a new Category and assign name based on folder
        newcategory = Category(categorypath.name,categorypath)        
        #get subfolder names in category directory
        categoryfolder = getsubdirs(newcategory.location)
        # itterate over the individual challenges
        for challengefolder in categoryfolder:
            challengefolderpath = Path(self.repofolder,categorypath.name, challengefolder)
            greenprint(f"[+] Found Challenge folder {challengefolderpath.name}")
            yellowboldprint(f'[+] {challengefolderpath}')
            try:
                # create new Challenge() class from folder contents
                newchallenge = self._createchallengefromfolder(challengefolderpath,newcategory.name)
                #assign challenge to category
            except Exception:
                errorlogger('[-] Error Creating Challenge!')
                continue
            
            newcategory._addchallenge(newchallenge)
        return newcategory
        
    def _createchallengefromfolder(self, challengefolderpath:Path,category:str) -> Challenge:
        '''
        Process the contents of the challenge folder given into a new Challenge() class
        This is essentially where the definition of a challenge folder itself
        is defined and parsed. You modify this to change that core specification

        Args:
            challengefolderpath (str): path to the challenge folder
            category (str): currently requires you specify the category
        '''
        challengedirlist = [challengedata for challengedata in os.listdir(os.path.normpath(challengefolderpath))]
        # get path to challenge subitem
        challengeitempath = lambda challengedata: Path(os.path.abspath(os.path.join(challengefolderpath,challengedata)))
        kwargs = {}
        contentslist = ["handout","solution","challenge"] #.yaml","challenge.yml"]
        # TODO: Flesh this out some for more validations
        try:
            # for list of all item in dir
            for item in challengedirlist:
                itempath = challengeitempath(item)
                # if the item is in the list of approved items
                if itempath.stem in contentslist:
                    greenprint(f"[+] Found : {item}")
                    kwargs[str(itempath.stem).lower()] =  itempath
                # if its a readme
                elif itempath.stem == "README":
                    kwargs[str(itempath.stem).lower()] = itempath
                # extra stuff not in approved list of contents
                elif itempath.stem not in contentslist:
                    # ignore it
                    continue
                # all other conditions
                else:
                    logger.error(f"[-] missing important item in challenge folder, skipping : missing {item}")
                    break
        except Exception:
            errorlogger("[-] ERROR: Challenge Folder contents do not conform to specification!")
        # generate challenge based on folder contents
        try:
            # start the linter
            linter = Linter()
            # process the challenge yaml file
            yamlcontents = Yaml.loadyaml(kwargs.pop("challenge"))
            # lint the challenge
            linter.lintchallengeyaml(yamlcontents)
            newchallenge = Challenge(
                category = category,
                handout= kwargs.pop('handout'),
                solution= kwargs.pop('solution'),
                readme = kwargs.get('README')
                )
            #load the challenge yaml dict into the class
            newchallenge._initchallenge(**yamlcontents)
            return newchallenge
        except Exception:
            errorlogger("[-] ERROR: Could not Create new Challenge from supplied data, Please check the log file")

    def _setcategory(self, repo:Repository, category:Category):
        """
        Adds a Category to the class
        We are adding classes to this class with "setattr"
        """
        setattr(repo, category.name, category)
        
    def _getcategory(self,repo:Repository, category:str)-> Category:
        """
        Returns The Category
        
        Args:
            repo (Repository) : Repository object created by masterlist
            category (str): the name of the category to return the challenges from
        
        Returns: 
        """
        # for each item in class
        for selfmember in dir(repo):
            # if its a Category, and not a hidden class attribute or function
            if (type(selfmember) == Category):#in CATEGORIES) and (selfmember.startswith("__") != True):
                return getattr(repo,selfmember)
                

    def listcategories(self):
        """
        Lists all categories
        """
        selflist = vars(self)
        categorylist = []
        for item in selflist:
            if type(item) == Category:
                categorylist.append(item)

    def removecategory(self, category:str):
        """
        Removes a category from the repository

        Args:

            category (str): Name of the category to unlink
        """

    def addcategory(self, category:Path):
        """
        Adds a Category to the repository

        Args:
            category (Path): path to category folder, in category level of repository
        """        
        #TODO: add entry to masterlist.yaml

    def synccategory(self):
        """
    Updates all challenges in CTFd with the versions in the repository
    Operates on the entire category 
        """
            #call 
    
    def _listchallenges(self):
        """
        Returns a list of all the installed challenges

        This is for local only, and is called by self.listchallenges()
        """

    def listchallenges(self, ctfdurl, ctfdtoken, remote=False):
        """
        NOT IMPLEMENTED YET

        Lists the challenges installed to the server
        Use 
        >>> --remote=False 
        to check the LOCAL repository
        For git operations, use `gitops` or your preferred terminal workflow

        Args:
            remote (bool): If True, Checks CTFd server for installed challenges
        """
        if remote == True:
            self.setauth(ctfdurl,ctfdtoken)#,adminusername,adminpassword)
            apicall = APIHandler( ctfdurl, ctfdtoken)
            challenges = apicall.get(apicall._getroute('challenges', admin=True), json=True).json()["data"]
            print(challenges)
        elif remote == False:
            #self.listsyncedchallenges()
            pass

    def removechallenge(self):
        """
        Removes a challenge from the repository
        Does not delete files, only unlinks
        """

    def syncchallenge(self):
        """
        
        """
    def updaterepository(self, challenge):
        """
    Updates the repository with any new content added to the category given
    if it doesnt fit the spec, it will issue an error    
    Try not to let your repo get cluttered
        """
