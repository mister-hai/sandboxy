
import os,re,sys
import threading
import yaml
import json
import gzip
import pathlib
import logging
import threading
import traceback
import subprocess
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

###############################################################################
#  CTFCLI HANDLING CLASS
###############################################################################

class SandBoxyCTFdLinkage():
    '''
    Uses ctfcli to upload challenges from the data directory in project root
    '''
    def __init__(self):
        # reflects the directory you have sandboxy in, default is ~/sandboxy
        self.PROJECTROOT=  os.getenv("PROJECTROOT",default=None)
        # reflects the data subdirectory in the project root
        self.DATAROOT= os.getenv("DATAROOT", default=None)
        # ctfd command line access variables
        self.CTFD_TOKEN          = os.getenv("CTFD_TOKEN", default=None)
        self.CTFD_URL            = os.getenv("CTFD_URL", default=None)

        #TODO: make challenges.yaml
        # folder expected to contain challenges
        self.challengesfolder    = os.path.join(self.DATAROOT, "challenges")
        # name of the yaml file expected to have the challenge data in each subfolder
        self.basechallengeyaml = "challenge.yml"
        # filename for the full challenge index
        self.listofchallenges    = "challengelist.yml"
        # filebuffer for challengelist.yaml
        self.challengelistbuffer = open(self.listofchallenges).read()
        self.challengelistyaml   = yaml.load(self.challengelistbuffer, Loader=yaml.FullLoader)
        
        ####################################
        #lambdas
        ##############
        # returns subdirectories , without . files/dirs
        self.getsubdirs = lambda directory: [name for name in os.listdir(directory) if os.path.isdir(name) and not re.match(r'\..*', name)]
        self.loadchallengeyaml =  lambda category,challenge: open(os.path.join(category,challenge,self.basechallengeyaml), 'r')

    def init(self):
        '''
        Initialize folder as repository with ctfcli using $CTFD_TOKEN and $CTFD_URL.
        '''
        if not self.CTFD_TOKEN or not self.CTFD_URL:
            exit(1)
        # run equivalent of  echo "$CTFD_URL\n$CTFD_TOKEN\ny" | ctf init 
        os.system(f"echo '{self.CTFD_URL}\n{self.CTFD_TOKEN}\ny' | ctf init")
    
    def get_categories(self,print:bool):
        '''
        Get the names of all Categories
        Supply "print=True" to display to screen instead of return a variable
        '''
        #old code
        #denylist_regex = r'\..*'
        #categories = [name for name in os.listdir(".") if os.path.isdir(name) and not re.match(denylist_regex, name)]
        categories = self.getsubdirs(self.challengesfolder)
        if print == True:
            greenprint("Categories: " + ", ".join(categories))
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

    def populateallchallenges(self):
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
            danglies

    def synccategory(category:str):
        '''
        Takes a category name

        Synchronize all challenges in the given category
        where each challenge is in it's own folder.
        '''
        challenges = [f"{category}/{name}" for name in os.listdir(f"./{category}") if os.path.isdir(f"{category}/{name}")]
        for challenge in challenges:
            if os.path.exists(f"{challenge}/challenge.yml"):
                print(f"Syncing challenge: {challenge}")
                os.system(f"ctf challenge sync '{challenge}'; ctf challenge install '{challenge}'")

    def syncchallenge(challenge:str):
        '''
        Adds a challenge
            Must be in its owwn folder, in a category that has been indexed
        '''
    def change_state(self, challenge:str, state:str):
        '''
        toggle challenge from visible to hidden
            This is obviously after the main list has been generated
        '''
        visible = {}
        hidden = {}
        try:
            if state not in ['visible', 'hidden']:
                raise Exception
        except Exception:
            errorlogger("[-] INVALID INPUT: {} {}".format(challenge,state))

        categories = self.get_categories()
        # maybe this would be better with dicts?
        for category in categories:
            visible[category] = []
            hidden[category] = []

        for challenges in self.challengelistyaml:
            #filter empties
            if challenge in challenges:
                # get category of challenge
                for category in self.challengelistyaml[challenge]:
                    # for each challenge in that category
                    for challenge in self.challengelistyaml[challenge][category]:
                        # read the challenge.yml file into a buffer
                        chall = self.loadchallengeyaml(category,challenge)

                        #challenge_yml = yaml.load(chall, Loader=yaml.FullLoader)
                        challenge_yml['state'] = state
                        if state == 'visible':
                            name = challenge_yml['name'].lower().replace(' ', '-')
                            if 'expose' in challenge_yml:
                                visible[category].append({'name': name, 'port': challenge_yml['expose'][0]['nodePort']})
                            else:
                                visible[category].append({'name': name, 'port': 0})
                        else:
                            if 'expose' in challenge_yml:
                                hidden[category].append({'name': name, 'port': challenge_yml['expose'][0]['nodePort']})
                            else:
                                hidden[category].append({'name': name, 'port': 0})
                        chall = open(f'{category}/{challenge}/challenge.yml', 'w')
                        yaml.dump(challenge_yml, chall, sort_keys=False)
            else:
                for category in self.challengelistyaml[wave]:
                    for challenge in self.challengelistyaml[wave][category]:
                        chall = open(f'{category}/{challenge}/challenge.yml', 'r')

                        challenge_yml = yaml.load(chall, Loader=yaml.FullLoader)
                        challenge_yml['state'] = 'hidden'
                        name = challenge_yml['name'].lower().replace(' ', '-')
                        if 'expose' in challenge_yml:
                            hidden[category].append({'name': name, 'port': challenge_yml['expose'][0]['nodePort']})
                        else:
                            hidden[category].append({'name': name, 'port': 0})
        return visible, hidden


###############################################################################
#  BEGIN MAIN FUNCTIONALITY
###############################################################################
#start a linkage
ctfdserver = SandBoxyCTFdLinkage()
#call the init funciton to connect
ctfdserver.init()
#danglies for nowsies
ctfdserver.synccategory()
ctfdserver.syncchallenge()

def change_state(self, challenge:str, state:str):
    '''
    toggle challenge from visible to hidden

    '''
    visible = {}
    hidden = {}
    try:
        if state not in ['visible', 'hidden']:
           raise Exception

    except Exception:
        errorlogger("[-] INVALID INPUT: {} {}".format(challenge,state))

    #self.challengelistyaml = open('challenge-waves.yml').read()
    #self.challengelistyaml = yaml.load(self.challengelistyaml, Loader=yaml.FullLoader)
    categories = self.get_categories()
    for category in categories:
        visible[category] = []
        hidden[category] = []

    for wave in self.challengelistyaml:
        if wave in waves:
            for category in self.challengelistyaml[wave]:
                for challenge in self.challengelistyaml[wave][category]:
                    chall = open(f'{category}/{challenge}/challenge.yml', 'r')

                    challenge_yml = yaml.load(chall, Loader=yaml.FullLoader)
                    challenge_yml['state'] = state

                    if state == 'visible':
                        name = challenge_yml['name'].lower().replace(' ', '-')
                        if 'expose' in challenge_yml:
                            visible[category].append({'name': name, 'port': challenge_yml['expose'][0]['nodePort']})
                        else:
                            visible[category].append({'name': name, 'port': 0})
                    else:
                        if 'expose' in challenge_yml:
                            hidden[category].append({'name': name, 'port': challenge_yml['expose'][0]['nodePort']})
                        else:
                            hidden[category].append({'name': name, 'port': 0})

                    chall = open(f'{category}/{challenge}/challenge.yml', 'w')

                    yaml.dump(challenge_yml, chall, sort_keys=False)
        else:
            for category in self.challengelistyaml[wave]:
                for challenge in self.challengelistyaml[wave][category]:
                    chall = open(f'{category}/{challenge}/challenge.yml', 'r')

                    challenge_yml = yaml.load(chall, Loader=yaml.FullLoader)
                    challenge_yml['state'] = 'hidden'
                    name = challenge_yml['name'].lower().replace(' ', '-')

                    if 'expose' in challenge_yml:
                        hidden[category].append({'name': name, 'port': challenge_yml['expose'][0]['nodePort']})
                    else:
                        hidden[category].append({'name': name, 'port': 0})


    return visible, hidden


# Firewall rules for visible challenges
def firewall(visible, hidden):
    rules = os.popen('gcloud compute firewall-rules --format=json list').read()

    for category in visible:
        for challenge in visible[category]:
            if challenge['port'] and challenge['name'] not in rules:
                os.system(
                    f"""
                        gcloud compute firewall-rules create {challenge['name']} \
                            --allow tcp:{challenge['port']} \
                            --priority 1000 \
                            --target-tags challs
                    """
                )
                print('Created firewall rules for:')
                print(challenge['name'])
    
    for category in hidden:
        for challenge in hidden[category]:
            if challenge['port'] and challenge['name'] in rules:
                os.system(
                    f"""
                        echo -e "Y\n" | gcloud compute firewall-rules delete {challenge['name']}
                    """
                )
                print('Deleted firewall rules for:')
                print(challenge['name'])    


# Synchronize each category in it's own thread.
if __name__ == "__main__":
    visible, hidden = change_state(['wave1', 'wave2'], 'visible')

    init()
    categories = get_categories()

    jobs = []
    for category in categories:
        jobs.append(threading.Thread(target=sync, args=(category, )))
    
    for job in jobs:
        job.start()

    for job in jobs:
        job.join()

    print("Synchronized successfully!")
    print("The following challenges are now visible:")

    for category in visible:
        print(f"\n{category}:")
        print('- ' + '\n- '.join([challenge['name'] for challenge in visible[category]]))

    firewall(visible, hidden)
    print("Firewall rules updated.")
