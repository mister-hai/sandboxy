import json
from pathlib import Path
from requests import Session
from utils import errorlogger,blueprint,yellowboldprint,redprint
from ctfdrepo import SandboxyCTFdRepository

class APISession(Session):
    def __init__(self, prefix_url:str, authtoken:str, *args, **kwargs):
        '''
        Represents a connection to the CTFd API
        '''
        #super(APISession, self).__init__(*args, **kwargs)
        # Strip out ending slashes and append a singular one so we generate
        # clean base URLs for both main deployments and subdir deployments
        #self.prefix_url = prefix_url.rstrip("/") + "/"
        self.CTFDURL = self.prefix_url
        self.AUTHTOKEN = authtoken

    #def request(self, method, url, *args, **kwargs):
        # Strip out the preceding / so that urljoin creates the right url
        # considering the appended / on the prefix_url
        #url = urljoin(self.prefix_url, url.lstrip("/"))
        #return super(APISession, self).request(method, url, *args, **kwargs)


    def getusers(self):
        ''' gets a list of all users'''

    def getvisibility(self, challenge, challenge_id):
        '''
        Gets the visibility of a challenge
        Hidden , Visible
        TODO: make it work
        '''
        response = self.get(f"/api/v1/challenges/{challenge_id}", json=json_payload)
        response.raise_for_status()

    def togglevisibility(self, challenge):
        '''
        Toggles a Challenge between hidden and visible
        '''
        try:
            challenge_id = challenge['challenge_id']
            if challenge.get("state") =="hidden":
                data = {"state": "visible"}
            if challenge.get("state") == "visible":
                data = {"state": "hidden"}
        # use requests.patch() to modify the value of a specific field on an existing APIcall.
        # PATCH differs from PUT in that it doesn’t completely replace the existing resource. 
        # It only modifies the values set in the JSON sent with the request.
            response = self.patch(f"/api/v1/challenges/{challenge_id}", json=data)
            response.raise_for_status()
        except Exception:
            errorlogger("[-] Failure To toggle challenge Visibility! Check the Logfiles!")
    
    def makevisible(self,challenge,challenge_id):
        '''
        Makes a Challenge Visible

        Args:
            challenge (str): The challenge to change state
        '''
    def makehidden(self, challenge):
        '''
        Makes a Challenge Hidden

        Args:
            challenge (str): The challenge to change state
        '''

    def processrequirements(self, challenge,challenge_id,data):
        '''
        Use a PATCH request to modify the Challenge Requirements
        '''
        installed_challenges = SandboxyCTFdRepository.listinstalledchallenges()
        required_challenges = []
        for requirements in challenge["requirements"]:
            if type(requirements) == str:
                for installedchallenge in installed_challenges:
                    if installedchallenge["name"] == requirements:
                        required_challenges.append(installedchallenge["id"])
            elif type(requirements) == int:
                required_challenges.append(requirements)
                required_challenges = list(set(required_challenges))
        data = {"requirements": {"prerequisites": required_challenges}}
        response = self.patch(f"/api/v1/challenges/{challenge_id}", json=data)
        response.raise_for_status()

    def processtags(self, challenge,challenge_id,data):
        for tag in challenge["tags"]:
            response =self.post("/api/v1/tags", json={"challenge_id": challenge_id, "value": tag})
            response.raise_for_status()

    def deleteremotehints(self, challenge_id,data):
        '''
        deletes all hints from ctfd
        HARD MODE: ON
        '''
        # Delete ALL existing hints
        current_hints = self.get(f"/api/v1/hints", json=data).json()["data"]
        for hint in current_hints:
            if hint["challenge_id"] == challenge_id:
                hint_id = hint["id"]
                response = self.delete(f"/api/v1/hints/{hint_id}", json=True)
                response.raise_for_status()

    def processhints(self, challenge,challenge_id,data):
        self.deleteexistinghints(challenge_id,data)
        # add hints
        for hint in challenge["hints"]:
            if type(hint) == str:
                data = {
                        "content"     : hint,
                        "cost"        : 0,
                        "challenge_id": challenge_id
                        }
            else:
                data = {
                        "content"      : hint["content"],
                        "cost"         : hint["cost"],
                        "challenge_id" : challenge_id
                        }
            response = self.post(f"/api/v1/hints", json=data)
            response.raise_for_status()

    def uploadfiles(self,challenge,challenge_id,data):
        '''
        uploads files to the ctfd server
        SAW ELSEWHERE IT HAD THIS
## Upload a file to a challenge.  You need to use a nonce from the admin page of the challenge you're editing.
nonce=$(curl -s http://127.0.0.1:8000/admin/challenges/1 -b cookie | grep nonce | cut -d'"' -f2)
curl -X POST "http://127.0.0.1:8000/api/v1/files" -b cookie  \
-F "file=@some-local-file.png" \
-F "nonce=$nonce" \
-F "challenge=1" \
-F "type=challenge"
        '''

        files = []
        for file in challenge["files"]:
            file_path = Path(challenge.directory, f)
            if file_path.exists():
                file_object = ("file", file_path.open(mode="rb"))
                files.append(file_object)
            else:
                raise Exception
        # Specifically use data= here instead of json= to send multipart/form-data
        r = self.post(f"/api/v1/files", files=files, data=self.json_payload)
        r.raise_for_status()

    def deleteremotefiles(self,file_path,data):
        '''
        deletes files from ctfd server
        '''
        try:
            # Delete existing files
            all_current_files =self.get(f"/api/v1/files?type=challenge", json=data).json()["data"]
            for file in all_current_files:
                for used_file in original_challenge["files"]:
                    if file["location"] in used_file:
                        file_id = file["id"]
                        r =self.delete(f"/api/v1/files/{file_id}", json=True)
                        r.raise_for_status()
        except Exception:
            errorlogger(f"File {file_path} was not found")

    def processtopics(self,challenge,challenge_id,data):
        # Delete existing tags
        current_tags = self.get(f"/api/v1/tags", json=data).json()["data"]
        for tag in current_tags:
            if tag["challenge_id"] == challenge_id:
                tag_id = tag["id"]
                response = self.delete(f"/api/v1/tags/{tag_id}", json=True)
                response.raise_for_status()

        for tag in challenge["tags"]:
            response = self.post(f"/api/v1/tags", json={"challenge_id": challenge_id, "value": tag})
            response.raise_for_status()

    def processtopics(self, challenge:dict, challenge_id, data):
        # Delete existing challenge topics
        current_topics = self.get(f"/api/v1/challenges/{challenge_id}/topics", json="").json()["data"]
        for topic in current_topics:
            topic_id = topic["id"]
            response = self.delete(f"/api/v1/topics?type=challenge&target_id={topic_id}", json=True)
            response.raise_for_status()
        # Add new challenge topics
        for topic in challenge["topics"]:
    #First, you create a dictionary containing the data for your apicall. 
    # Then you pass this dictionary to the json keyword argument of requests.post(). 
    # When you do this, requests.post() automatically sets the request’s HTTP header 
    # Content-Type to application/json. It also serializes todo into a JSON string, 
    # which it appends to the body of the request.
    # If you don’t use the json keyword argument to supply the JSON data, then you 
    # need to set Content-Type accordingly and serialize the JSON manually.
            response =self.post(f"/api/v1/topics",json={"value": topic,"type": "challenge","challenge_id": challenge_id,})
            response.raise_for_status()

    def processflags(self, challenge:dict, challenge_id, data):
        current_flags = self.get(f"/api/v1/flags", json=data).json()["data"]
        for flag in current_flags:
            if flag["challenge_id"] == challenge_id:
                flag_id = flag["id"]
                response = self.delete(f"/api/v1/flags/{flag_id}", json=True)
        for flag in challenge["flags"]:
            if type(flag) == str:
                data = {"content": flag, "type": "static", "challenge_id": challenge_id}
                response = self.post(f"/api/v1/flags", json=data)
                response.raise_for_status()
            elif type(flag) == dict:
                flag["challenge_id"] = challenge_id
                response = self.post(f"/api/v1/flags", json=flag)
                response.raise_for_status()
   
    def was_there_was_an_error(self, responsecode):
        ''' Returns False if no error'''
        # server side error]
        set1 = [404,504,503,500]
        set2 = [400,405,501]
        set3 = [500]
        if responsecode in set1 :
            blueprint("[-] Server side error - No Resource Available in REST response")
            yellowboldprint("Error Code {}".format(responsecode))
            return True # "[-] Server side error - No resource Available in REST response"
        if responsecode in set2:
            redprint("[-] User error in Request")
            yellowboldprint("Error Code {}".format(responsecode))
            return True # "[-] User error in Image Request"
        if responsecode in set3:
            #unknown error
            blueprint("[-] Unknown Server Error - No Resource Available in REST response")
            yellowboldprint("Error Code {}".format(responsecode))
            return True # "[-] Unknown Server Error - No Image Available in REST response"
        # no error!
        if responsecode == 200:
            return False