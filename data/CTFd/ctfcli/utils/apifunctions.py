from utils.apisession import APISession
from utils.utils import errorlogger

class APIFunctions(APISession):
    """
    Functions Specific to CTFd
    """
    def __init__(self):
        pass

    def getusers(self):
        """ gets a list of all users"""

    def getvisibility(self, challengeid, jsonpayload):
        """
        Gets the visibility of a challenge
        >>> {"state": "visible"}
        state can be Hidden or Visible
        TODO: make it work
        """
        return self.get(f"/api/v1/challenges/{challengeid}").json() #, json=jsonpayload).json()

    def togglevisibility(self, challenge_id):
        """
        Toggles a Challenge between hidden and visible
        """
        try:
            challenge = self.getvisibility(challenge_id)
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
    
    def makevisible(self,challenge_id):
        """
        Makes a Challenge Visible

        Args:
            challenge (str): The challenge to change state
        """
        data = {"state": "visible"}
        response = self.patch(f"/api/v1/challenges/{challenge_id}", json=data)
        response.raise_for_status()

    def makehidden(self, challenge_id):
        """
        Makes a Challenge Hidden

        Args:
            challenge (str): The challenge to change state
        """
        data = {"state": "hidden"}
        response = self.patch(f"/api/v1/challenges/{challenge_id}", json=data)
        response.raise_for_status()

    def processrequirements(self, challenge, requirements, challenge_id):
        """
        Use a PATCH request to modify the Challenge Requirements
        """

        for reqs in challenge.requirements:
            if type(reqs) == str:
                required_challenges.append(reqs)
            elif type(requirements) == int:
                #why? I'll leave it for now
                required_challenges.append(reqs)
                required_challenges = list(set(required_challenges))
        data = {"requirements": {"prerequisites": required_challenges}}
        response = self.patch(f"/api/v1/challenges/{challenge_id}", json=data)
        response.raise_for_status()

    def processtags(self, challenge,challenge_id,data):
        for tag in challenge["tags"]:
            response =self.post("/api/v1/tags", json={"challenge_id": challenge_id, "value": tag})
            response.raise_for_status()

    def gethints(self)-> dict:
        """
        gets hints for specific challenge from server
        """
        return self.get(f"/api/v1/hints", json=data).json()["data"]

    def deleteremotehints(self, challenge_id,data):
        """
        deletes all hints from ctfd
        HARD MODE: ON
        """
        # Delete ALL existing hints
        current_hints = self.get(f"/api/v1/hints", json=data).json()["data"]
        for hint in current_hints:
            hint_id = hint["id"]
            apicall = self.delete(f"/api/v1/hints/{hint_id}", json=True)
        apicall.raise_for_status()
        # deletes specific hint
            #if hint["challenge_id"] == challenge_id:
            #    hint_id = hint["id"]
            #    response = self.delete(f"/api/v1/hints/{hint_id}", json=True)
            #    response.raise_for_status()

    def deletehints(self):
        """
        Deletes specific challenge hints
        """
        current_hints = self.get(f"/api/v1/hints", json=data).json()["data"]
        for hint in current_hints:
            hint_id = hint["id"]
            if hint["challenge_id"] == challenge_id:
                hint_id = hint["id"]
                response = self.delete(f"/api/v1/hints/{hint_id}", json=True)
                response.raise_for_status()


    def synchints(self,challenge_id,data):
        """
        Syncs hints with ctfd server
        """
        self.deletehints(challenge_id,data)
        # add hints
        for hint in challenge.hints:
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
   
    def uploadfiles(self,challenge,challenge_id,data):
        """
        uploads files to the ctfd server
        SAW ELSEWHERE IT HAD THIS
        >>> ## Upload a file to a challenge.  You need to use a nonce from the admin page of the challenge you're editing.
        >>> nonce=$(curl -s http://127.0.0.1:8000/admin/challenges/1 -b cookie | grep nonce | cut -d'"' -f2)
        >>> curl -X POST "http://127.0.0.1:8000/api/v1/files" -b cookie  \
        >>> -F "file=@some-local-file.png" \
        >>> -F "nonce=$nonce" \
        >>> -F "challenge=1" \
        >>> -F "type=challenge"
        """

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
        """
        deletes files from ctfd server
        """
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
