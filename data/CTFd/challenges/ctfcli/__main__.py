import re
import git
import fire
import json
import yaml
import os, sys
import importlib
import subprocess
import configparser
from pathlib import Path
from requests import Session
from urllib.parse import urljoin
from urllib.parse import urlparse
from cookiecutter.main import cookiecutter

from pygments import highlight
from pygments.formatters import TerminalFormatter
from pygments.lexers import IniLexer, JsonLexer

from utils.config import get_config_path, preview_config

from utils.challenge import (
    create_challenge,
    lint_challenge,
    load_challenge,
    load_installed_challenges,
    sync_challenge,
)

from utils.deploy import DEPLOY_HANDLERS
from utils.spec import CHALLENGE_SPEC_DOCS, blank_challenge_spec
# move to this file
#from .utils.plugins import get_plugin_dir
import logging
import threading
import traceback
import subprocess
import pathlib
import sys

try:
    import colorama
    from colorama import init
    init()
    from colorama import Fore, Back, Style
    COLORMEQUALIFIED = True
except ImportError as derp:
    print("[-] NO COLOR PRINTING FUNCTIONS AVAILABLE, Install the Colorama Package from pip")
    COLORMEQUALIFIED = False

################################################################################
##############               LOGGING AND ERRORS                #################
################################################################################
LOGLEVEL            = 'DEV_IS_DUMB'
LOGLEVELS           = [1,2,3,'DEV_IS_DUMB']
log_file            = 'logfile'
logging.basicConfig(filename=log_file, format='%(asctime)s %(message)s', filemode='w')
logger              = logging.getLogger()
launchercwd         = pathlib.Path().absolute()


redprint          = lambda text: print(Fore.RED + ' ' +  text + ' ' + Style.RESET_ALL) if (COLORMEQUALIFIED == True) else print(text)
blueprint         = lambda text: print(Fore.BLUE + ' ' +  text + ' ' + Style.RESET_ALL) if (COLORMEQUALIFIED == True) else print(text)
greenprint        = lambda text: print(Fore.GREEN + ' ' +  text + ' ' + Style.RESET_ALL) if (COLORMEQUALIFIED == True) else print(text)
yellowboldprint = lambda text: print(Fore.YELLOW + Style.BRIGHT + ' {} '.format(text) + Style.RESET_ALL) if (COLORMEQUALIFIED == True) else print(text)
makeyellow        = lambda text: Fore.YELLOW + ' ' +  text + ' ' + Style.RESET_ALL if (COLORMEQUALIFIED == True) else text
makered           = lambda text: Fore.RED + ' ' +  text + ' ' + Style.RESET_ALL if (COLORMEQUALIFIED == True) else None
makegreen         = lambda text: Fore.GREEN + ' ' +  text + ' ' + Style.RESET_ALL if (COLORMEQUALIFIED == True) else None
makeblue          = lambda text: Fore.BLUE + ' ' +  text + ' ' + Style.RESET_ALL if (COLORMEQUALIFIED == True) else None
debuglog     = lambda message: logger.debug(message) 
infolog      = lambda message: logger.info(message)   
warninglog   = lambda message: logger.warning(message) 
errorlog     = lambda message: logger.error(message) 
criticallog  = lambda message: logger.critical(message)

################################################################################
##############             ERROR HANDLING FUNCTIONS            #################
################################################################################
def errorlogger(message):
    '''
    prints line number and traceback
    TODO: save stack trace to error log
            only print linenumber and function failure
    '''
    exc_type, exc_value, exc_tb = sys.exc_info()
    trace = traceback.TracebackException(exc_type, exc_value, exc_tb) 
    try:
        errormesg = message + ''.join(trace.format_exception_only())
        #traceback.format_list(trace.extract_tb(trace)[-1:])[-1]
        lineno = 'LINE NUMBER >>>' + str(exc_tb.tb_lineno)
        errorlog(lineno+errormesg)
    except Exception:
        print("EXCEPTION IN ERROR HANDLER!!!")
        print(message + ''.join(trace.format_exception_only()))
class APISession(Session):
    def __init__(self, prefix_url=None, *args, **kwargs):
        super(APISession, self).__init__(*args, **kwargs)
        # Strip out ending slashes and append a singular one so we generate
        # clean base URLs for both main deployments and subdir deployments
        self.prefix_url = prefix_url.rstrip("/") + "/"

    def request(self, method, url, *args, **kwargs):
        # Strip out the preceding / so that urljoin creates the right url
        # considering the appended / on the prefix_url
        url = urljoin(self.prefix_url, url.lstrip("/"))
        return super(APISession, self).request(method, url, *args, **kwargs)
###############################################################################
## Config class
## Maps to the command
## host@server$> ctfcli challenge config <command>
###############################################################################
class Config():
    def __init__(self):
        pass
    def loadconfig(self):
        '''
        loads.config.ini
        '''

    def edit(self):
        '''
        ctfcli config edit
            Edit config with $EDITOR
        '''
        editor = os.getenv("EDITOR", "vi")
        command = editor, get_config_path()
        subprocess.call(command)

    def path(self):
        '''
        ctfcli config path
            Show config path
        '''
        click.echo(get_config_path())

    def view(self, color=True, json=False):
        '''
        ctfcli config view
            view the config
        '''
        config = get_config_path()
        with open(config) as f:
            if json is True:
                config = preview_config(as_string=True)
                if color:
                    config = highlight(config, JsonLexer(), TerminalFormatter())
            else:
                config = f.read()
                if color:
                    config = highlight(config, IniLexer(), TerminalFormatter())
            print(config)

###############################################################################
## Git interactivity class
###############################################################################
class SandboxyCTFdRepository():
    '''
    
    '''
    def __init__(self, repo, clone=False):
        self.repo = repo
        if clone == True:
            try:
                # the user indicates a remote repo, by supplying a url
                if re.match(r'^(?:http|https)?://', self.repo) or repo.endswith(".git"):
                    self.repository = git.Repo.clone(self.repo)
                    # get remote references to sync repos
                    self.heads = self.repository.heads
                    # get reference for master branch
                    # lists can be accessed by name for convenience
                    self.master = self.heads.master
                    # Get latest coommit
                    # the commit pointed to by head called master
                    self.mastercommit = self.master.commit
                #the user indicates the challenge folder is to be the repository
                # this is the expected action
                elif clone == False:
                    self.repository = git.Repo.init(path=self.repo)
            except Exception:
                errorlogger("[-] ERROR: Could not create Git repository in the challenges folder")

        #all all files in challenge folder to local repository
        self.repository.index.add()
        self.repository.index.commit('Initial commit')
        self.repository.create_head('master')
    
    def cloneremote(self,repourl):
        '''
        Clones Remote Repository into challenge directory
        '''

class GitOperations():
    ''' Added to FIREPL
Git interactivity class, Maps to the command
>>> host@server$> ctfcli gitoperations <command>

Available Commands:
    - createrepo
        initiates a new repository in the challenges folder
        adds all files in challenges folder to repo
    - 
    - 
    '''
    def __init__(self):
        pass

    def createrepo(self, repo:str):
        """
Create a git repository with a ``master`` branch and ``README``.
    This function will create a new local repository
        """
        newrepo = SandboxyCTFdRepository()


###############################################################################
#  CTFCLI HANDLING CLASS
###############################################################################
class ChallengeCategory():
    '''
    use getattr(),setattr() to add/query Challenge Entries
    this is used for keeping track internally

    ChallengeCategory:
        represents a folder in the PROJECTDIRECTORY/data/CTFd/challenges/ dir
      ChallengeEntry:
        represents a challenge.yaml
        name: thing
      ChallengeEntry:
        represents a challenge.yaml
        name: thing
      ChallengeEntry:
        represents a challenge.yaml
        name: thing

    '''
    def __init__(self,name):
        self.name = name
        self.testchallenge = setattr(self,Challenge("test.yaml"))
    
    def addchallenge(self, challenge):
        '''
        Adds a challenge to the category
        '''

class Yaml(dict):
    '''
    Represents a challange.yml
    Give Path to challenge.yaml
    '''
    def __init__(self,data, filepath):
        #set the base values
        self.type = str
        #get path of file
        self.filepath = Path(filepath)
        #set working dir of file
        self.directory = self.filepath.parent
        #if its a kubernetes config
        if self.filepath.endswith(".yaml"):
            redprint("[!] File is .yaml! Presuming to be kubernetes config!")
            self.type = "kubernetes"
        else:
            greenprint("[+] Challenge File presumed (.yml)")
            try:
                #open the yml file
                with open(filepath) as f:
                    filedata = yaml.safe_load(f.read(), filepath=filepath)
                    #assign data to self
                    #previous
                    #super().__init__(filedata)
                    setattr(self,"data",filedata)
            except FileNotFoundError:
                print("No challenge.yml was found in {}".format(filepath))

class KubernetesSpec():
    '''
    Represents a Kubernetes specification
    '''
    def __init__(self):
        pass

class Challenge():
    '''
    Represents the challenge as exists in the folder for that specific challenge
    '''
    def __init__(self,yamlfile:Yaml):
        #get a representation of the challenge.yaml file
        self.challengeyaml = yamlfile
        self.yamldata = self.challengeyaml.data
        # name of the challenge
        self.name        = self.challengeyaml['name']
        self.author      = self.challengeyaml['author']
        self.category    = self.challengeyaml['category']
        self.description = self.challengeyaml['description']
        self.value       = self.challengeyaml['value']
        self.type        = self.challengeyaml['type']

class ChallengeFolder():
    '''
    Represents the Challenge folder
    '''
    def __init__(self, templatesdir):
        pass

    def load_challenge(self,path):
        try:
            with open(path) as f:
                return Yaml(data=yaml.safe_load(f.read()), file_path=path)
        except FileNotFoundError:
            errorlogger("No challenge.yml was found in {}".format(path))
            return

    def install(self, challenge:str, force=False, ignore=()):
        '''
        Installs a challenge from a folder
        takes a path to a challenge.yml
        '''
        challenge = self.load_challenge(challenge)
        print(f'Loaded {challenge["name"]}', fg="yellow")
        installed_challenges = load_installed_challenges()
        for chall in installed_challenges:
            if chall["name"] == challenge["name"]:
                yellowboldprint("Already found existing challenge with same name \
                    ({}). Perhaps you meant sync instead of install?".format(challenge['name']))
                if force is True:
                    yellowboldprint("Ignoring existing challenge because of --force")
                else:
                        break
            else:  # If we don't break because of duplicated challenge names
                print(f'Installing {challenge["name"]}', fg="yellow")
                create_challenge(challenge=challenge, ignore=ignore)
                print("Success!", fg="green")

    def sync(self, challenge=None, ignore=()):
        if challenge is None:
            # Get all challenges if not specifying a challenge
            challenges = dict(config["challenges"]).keys()
        else:
            challenges = [challenge]

        if isinstance(ignore, str):
            ignore = (ignore,)

        for challenge in challenges:
            path = Path(challenge)

            if path.name.endswith(".yml") is False:
                path = path / "challenge.yml"

            print("Found {path}")
            challenge = load_challenge(path)
            print(f'Loaded {challenge["name"]}', fg="yellow")

            installed_challenges = load_installed_challenges()
            for c in installed_challenges:
                if c["name"] == challenge["name"]:
                    break
            else:
                print(f'Couldn\'t find existing challenge {c["name"]}. Perhaps you meant install instead of sync?')
                continue  # Go to the next challenge in the overall list

            print(f'Syncing {challenge["name"]}', fg="yellow")
            sync_challenge(challenge=challenge, ignore=ignore)
            print("Success!", fg="green")

#    def update(self, challenge=None):
#        for folder, url in challenges.items():
#            if url.endswith(".git"):
#                click.echo(f"Pulling latest {url} to {folder}")
#                head_branch = get_git_repo_head_branch(url)
#                subprocess.call(["git","subtree","pull","--prefix",folder,url,head_branch,"--squash",],cwd=self.CH,)
#                subprocess.call(["git", "mergetool"], cwd=folder)
#                subprocess.call(["git", "clean", "-f"], cwd=folder)
#                subprocess.call(["git", "commit", "--no-edit"], cwd=folder)
#            else:
#                click.echo(f"Skipping {url} - {folder}")

    def finalize(self, challenge=None):
        if challenge is None:
            challenge = os.getcwd()

        path = Path(challenge)
        spec = blank_challenge_spec()
        for k in spec:
            q = CHALLENGE_SPEC_DOCS.get(k)
            fields = q._asdict()

            ask = False
            required = fields.pop("required", False)
            if required is False:
                try:
                    ask = click.confirm(f"Would you like to add the {k} field?")
                    if ask is False:
                        continue
                except click.Abort:
                    click.echo("\n")
                    continue

            if ask is True:
                fields["text"] = "\t" + fields["text"]

            multiple = fields.pop("multiple", False)
            if multiple:
                fields["text"] += " (Ctrl-C to continue)"
                spec[k] = []
                try:
                    while True:
                        r = click.prompt(**fields)
                        spec[k].append(r)
                except click.Abort:
                    click.echo("\n")
            else:
                try:
                    r = click.prompt(**fields)
                    spec[k] = r
                except click.Abort:
                    click.echo("\n")
        with open(path / "challenge.yml", "w+") as f:
            yaml.dump(spec, stream=f, default_flow_style=False, sort_keys=False)
        print("challenge.yml written to", path / "challenge.yml")

    def lint(self, challenge=None):
        path = Path(challenge)
        lint_challenge(path)

    def deploy(self, challenge, host=None):
        if challenge is None:
            challenge = os.getcwd()

        path = Path(challenge)

        if path.name.endswith(".yml") is False:
            path = path / "challenge.yml"

        challenge = load_challenge(path)
        image = challenge.get("image")
        target_host = host or challenge.get("host") or input("Target host URI: ")
        if image is None:
            print("This challenge can't be deployed because it doesn't have an associated image")
            return
        if bool(target_host) is False:
            print("This challenge can't be deployed because there is no target host to deploy to")
            return
        url = urlparse(target_host)

        if bool(url.netloc) is False:
            print("Provided host has no URI scheme. Provide a URI scheme like ssh:// or registry://")
            return

        status, domain, port = DEPLOY_HANDLERS[url.scheme](challenge=challenge, host=target_host)
        if status:
            greenprint("[+] Challenge deployed at {}:{}".format(domain,port))
        else:
            redprint("[-] ERROR: deployment failed! Check the logfile!")



###############################################################################
## MAIN class
## Maps to the command
## host@server$> ctfcli
# run on it's own to produce help text
###############################################################################
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

    #def loadplugins(self):
    #    '''
    #    Loads Plugins from cli directory
    #        files must end in .py and have simple, descriptive names
    #        settattr is being used, no funny business!
    #    '''
    #    #loads files from the /ctfcli/cli directory for use as
    #    # REPL interface objects
    #    greenprint("[+] Loading Plugins from {}".format(self.PLUGINDIRECTORY))
    #    # for each of the files in the plugin directory
    #    for replimport in sorted(os.listdir(self.PLUGINDIRECTORY)):
    #        # get an absolute path to the file
    #        filepath = os.path.join(self.PLUGINDIRECTORY, replimport)
    #        greenprint("Loading {}".format(replimport))
    #        #import that file
    #        importedmodule = importlib.import_module(filepath)
    #        # add specified modules into class
    #        setattr(self,replimport,importedmodule)

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
            # TODO: write list of challenges to yaml with tags
                danglies

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
                #old code
                danglies
                #os.system(f"ctf challenge sync '{challenge}'; ctf challenge install '{challenge}'")
        except Exception:
            errorlogger("[-] Failure, INPUT: {}".format(challenge))

    def syncchallenge(challenge:str):
        '''
        Adds a challenge
            Must be in its own folder, in a category that has been indexed
        '''
        greenprint(f"Syncing challenge: {challenge}")
        try:
            #old code
            danglies
            #os.system(f"ctf challenge sync '{challenge}'; ctf challenge install '{challenge}'")
        except Exception:
            errorlogger("[-] Failure, INPUT: {}".format(challenge))


    def generate_session(self):
        config = load_config()
        url = config["config"]["url"]
        access_token = config["config"]["access_token"]
        s = APISession(prefix_url=url)
        s.headers.update({"Authorization": f"Token {access_token}"})
        return s

    def load_installed_challenges(self):
        s = self.generate_session()
        return s.get("/api/v1/challenges?view=admin", json=True).json()["data"]

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
#class Menu():
#    '''
#    Shows a useful menu for the users to operate with on the commmand line
#    '''
#    def __init__(self):
#        pass
#    def main(self):
#        pass


if __name__ == "__main__":
    menu = Menu()
    menu.main()
    # Load CLI
    fire.Fire(SandBoxyCTFdLinkage)
