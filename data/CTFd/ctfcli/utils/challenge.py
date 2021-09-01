import requests
import subprocess
from Yaml import Yaml
from pathlib import Path

from apicalls import APISession
from ctfdrepo import SandboxyCTFdRepository
from utils import errorlogger,yellowboldprint,greenprint

class Challenge(): #folder
    '''

    '''
    def __init__(self, 
                name,
                category,
                location, 
                challengefile, 
                #challengesrc,
                #deployment,
                handout,
                solution
                ):
        self.name               = str
        self.category           = category
        # path to challenge folder
        self.challengelocation  = location
        # path to challenge.yml file
        self.challengefile      = challengefile
        # folder
        self.solutiondir        = solution
        # folder
        self.handout            = handout
        # folder
        #self.challengesrc       = challengesrc
        #self.deployment         = deployment
        self.id = 1
        self.type = str
        self.name = str
        self.value = 500
        self.solves = 0
        self.solved_by_me = "false"
        self.category = str
        self.tags = []
        self.template = str
        self.script =  str
    

class ChallengeActions(Challenge):
    def install(self, challenge:str, force=False, ignore=()):
        '''
        Installs a challenge from a folder into the repository
        to add it to the ctfd server, use "sync"
        takes a path to a challenge.yml
        '''
        challenge = self.load_challenge(challenge)
        print(f'Loaded {challenge["name"]}')
        installed_challenges = SandboxyCTFdRepository.listinstalledchallenges()
        for chall in installed_challenges:
            if chall["name"] == challenge["name"]:
                yellowboldprint("Already found existing challenge with same name \
                    ({}). Perhaps you meant sync instead of install?".format(challenge['name']))
                if force is True:
                    yellowboldprint("Ignoring existing challenge because of --force")
                else:
                    break
            else:  # If we don't break because of duplicated challenge names
                print(f'Installing {challenge["name"]}')
                SandboxyCTFdRepository.addchallenge(challenge=challenge, ignore=ignore)
                print("Success!", fg="green")

    def sync(self): #, challenge=None, ignore=()):
            #challenge = self.load_challenge(challenge)
            #greenprint('Loaded {}'.format(challenge["name"]))

            #get list of all challenges
            installedchallenges = SandboxyCTFdRepository.loadinstalledchallenges()
            for challenge in installedchallenges:
                #check if challenge is synced
                if challenge.synced == True:
                    danglies
                    pass
            else:
                print(f'Couldn\'t find existing challenge {c["name"]}. Perhaps you meant install instead of sync?')

            print(f'Syncing {challenge["name"]}', fg="yellow")
            self.syncchallenge(challenge=challenge)


    def syncchallenge(self,challenge:dict):
        '''
        Adds a challenge to CTFD
            Must be in its own folder, in a category that has been indexed
        
        This command is to be run on single challenge folders
        This command is called RECURSIVELY by other code, referece its input and output
        '''
        greenprint(f"Syncing challenge: {challenge}")
        getchallengebyname(challenge)

        #TOTO SET CHALLENGE ID
        challenge_id = str
        try:
            #assign data fields to json
            challengevalue       = int(challenge["value"]) if challenge["value"] else challenge["value"],challenge.get("extra", {})
            challengetype        = challenge.get("type", "standard")
            challengedescription = challenge["description"]
            challengecategory    = challenge["category"]
            challengename        = challenge["name"]
            challengeauthor      = challenge["author"]
            # Some challenge types (e.g. dynamic) override value.
            # We can't send it to CTFd because we don't know the current value
            if challenge["value"] is None:
                del challenge["value"]
                json_payload = {
                "name":         challengename,
                "category":     challengecategory,
                "description":  challengedescription,
                "type":         challengetype,
                "value" :       challengevalue,
                "author" :      challengeauthor
                }
            if challenge.get("attempts"):
                json_payload["max_attempts"] = challenge.get("attempts")
            if challenge.get("connection_info"):
                json_payload["connection_info"] = challenge.get("connection_info")
            try:
                #make API call
                apicall = APISession(prefix_url=self.CTFD_URL)
                # auth to server
                apicall.headers.update({"Authorization": "Token {}".format(apicall.AUTHTOKEN)})
                # check for challenge install
                apisess = apicall.get("/api/v1/challenges/{}".format(challenge_id), json=json_payload).json()["data"]
                # use requests.patch() to modify the value of a specific field on an existing APIcall.
                # why are they patching the challenge ID?
                response = apisess.patch(f"/api/v1/challenges/{challenge_id}", json=json_payload)
                response.raise_for_status()
            except requests.exceptions.HTTPError as errh:
                print(errh)
            except requests.exceptions.ConnectionError as errc:
                print(errc)
            except requests.exceptions.Timeout as errt:
                print(errt)
            except requests.exceptions.RequestException as err:
                print(err)
            # Create new flags
            if challenge.get("flags"):
                apicall.processflags(challenge,challenge_id,json_payload)
            # Update topics
            if challenge.get("topics"):
                apicall.processtopics(challenge,challenge_id,json_payload)
            # Update tags
            if challenge.get("tags"):
                apicall.processtopics(challenge,challenge_id,json_payload)
            # Upload files
            if challenge.get("files"):
                apicall.uploadfiles(challenge,challenge_id,json_payload)
            # Create hints
            if challenge.get("hints"):
                apicall.processhints(challenge,challenge_id,json_payload)
            # Update requirements
            if challenge.get("requirements"):
                apicall.processrequirements(challenge,challenge_id,json_payload)

            #if challenge.get["state"] =="visible":
        except Exception:
            errorlogger("[-] ERROR! FAILED TO SYNCRONIZE CHALLENGE WITH SERVER")

def create_challenge(challenge, ignore=[]):
    json_payload = {
            "name":         challenge["name"],
            "category":     challenge["category"],
            "description":  challenge["description"],
            "type":         challenge.get("type", "standard"),
            "value":        int(challenge["value"]) if challenge["value"] else challenge["value"],
            **challenge.get("extra", {})
            }
    # Some challenge types (e.g. dynamic) override value.
    # We can't send it to CTFd because we don't know the current value
    if challenge["value"] is None:
        del challenge["value"]
    if challenge.get("attempts"):
        json_payload["max_attempts"] = challenge.get("attempts")
    if challenge.get("connection_info"):
        json_payload["connection_info"] = challenge.get("connection_info")
    
    apicall = APISession()
    response = apicall.post("/api/v1/challenges", json=json_payload)
    response.raise_for_status()
    challenge_data = response.json()
    challenge_id = challenge_data["data"]["id"]
    # Create flags
    if challenge.get("flags"):
        apicall.processflags(challenge, challenge_id, json_payload)
    # Create topics
    if challenge.get("topics"):
        apicall.processtopics(challenge, challenge_id, json_payload)
        # Create tags
    if challenge.get("tags"):
        apicall.processtags(challenge,challenge_id,json_payload)
        # Upload files
    if challenge.get("files"):
        apicall.uploadfiles(challenge,challenge_id,json_payload)
    # Add hints
    if challenge.get("hints"):
        apicall.processhints()
    # Add requirements
    if challenge.get("requirements") and "requirements" not in ignore:
        apicall.processrequirements(challenge,challenge_id,json_payload)
    # Set challenge state
    if challenge.get("state"):
            json_payload["state"] = challenge["state"]
            apicall. challenge_id}", json=json_payload))
            r.raise_for_status()


    def lint_challenge(self, challengefilepath):
        required_fields = ["name", "author", "category", "description", "value"]
        errors = []
        for field in required_fields:
            if field == "value" and challenge.get("type") == "dynamic":
                pass
            else:
                if challenge.get(field) is None:
                    errors.append(field)
        if len(errors) > 0:
            print("Missing fields: ", ", ".join(errors))
            exit(1)
        # Check that the image field and Dockerfile match
        if (Path(challengefilepath).parent / "Dockerfile").is_file() and challenge.get("image") != ".":
            print("Dockerfile exists but image field does not point to it")
            exit(1)
        # Check that Dockerfile exists and is EXPOSE'ing a port
        if challenge.get("image") == ".":
            try:
                dockerfile = (Path(path).parent / "Dockerfile").open().read()
            except FileNotFoundError:
                print("Dockerfile specified in 'image' field but no Dockerfile found")
                exit(1)
            if "EXPOSE" not in dockerfile:
                print("Dockerfile missing EXPOSE")
                exit(1)
            # Check Dockerfile with hadolint
            proc = subprocess.run(
                ["docker", "run", "--rm", "-i", "hadolint/hadolint"],
                input=dockerfile.encode(),
            )
            if proc.returncode != 0:
                print("Hadolint found Dockerfile lint issues, please resolve")
                exit(1)
        # Check that all files exists
        files = challenge.get("files", [])
        errored = False
        for f in files:
            fpath = Path(path).parent / f
            if fpath.is_file() is False:
                print(f"File {f} specified but not found at {fpath.absolute()}")
                errored = True
        if errored:
            exit(1)
    exit(0)
