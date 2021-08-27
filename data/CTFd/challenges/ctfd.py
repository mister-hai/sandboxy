
import os,re,sys
import threading
import yaml
import pathlib


class SandBoxyCTFdLinkage():
    '''
    Uses ctfcli to upload challenges from the data directory in project root
    '''
    def __init__(self):
        # set by .env and start.sh
        # reflects the directory you have sandboxy in, default is ~/sandboxy
        self.PROJECTROOT=  os.getenv("PROJECTROOT",default=None)
        # set by .env and start.sh
        # reflects the data subdirectory in the project root
        self.DATAROOT= os.getenv("DATAROOT", default=None)
        # set by .env and start.sh
        # ctfd command line access variables
        self.CTFD_TOKEN          = os.getenv("CTFD_TOKEN", default=None)
        self.CTFD_URL            = os.getenv("CTFD_URL", default=None)

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

    def init(self):
        '''
        Initialize PWD as repository with ctfcli using $CTFD_TOKEN and $CTFD_URL.
        '''
        if not self.CTFD_TOKEN or not self.CTFD_URL:
            errorlogger("[-] NO INPUT, something is wrong")
            exit(1)
        try:
            # run equivalent of  echo "$CTFD_URL\n$CTFD_TOKEN\ny" | ctf init 
            os.system(f"echo '{self.CTFD_URL}\n{self.CTFD_TOKEN}\ny' | ctf init")
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
                        challengeyaml = self.loadchallengeyaml(category,challenge)
                        # obtain state of the challenge
                        challengeyaml['state'] = state
                        # toggle to invisible
                        if state == 'visible':
                            name = challengeyaml['name'].lower().replace(' ', '-')
                            if 'expose' in challenge_yml:
                                visible[category].append({'name': name, 'port': challenge_yml['expose'][0]['nodePort']})
                            else:
                                visible[category].append({'name': name, 'port': 0})
                        else:
                            if 'expose' in challenge_yml:
                                hidden[category].append({'name': name, 'port': challenge_yml['expose'][0]['nodePort']})
                            else:
                                hidden[category].append({'name': name, 'port': 0})
                        chall = self.readchallengeintobuffer(category,challenge)
                        yaml.dump(challengeyaml, chall, sort_keys=False)
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
