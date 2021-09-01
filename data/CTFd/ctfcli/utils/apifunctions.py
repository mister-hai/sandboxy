
class APIFunctions():
    '''
    Functions Specific to CTFd
    '''
    def __init__(self):
        pass

    def getusers(self):
        """ gets a list of all users"""

    def getvisibility(self, challenge, challenge_id):
        """
        Gets the visibility of a challenge
        Hidden , Visible
        TODO: make it work
        """
        response = self.get(f"/api/v1/challenges/{challenge_id}", json=json_payload)
        response.raise_for_status()

    def togglevisibility(self, challenge):
        """
        Toggles a Challenge between hidden and visible
        """
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
        """
        Makes a Challenge Visible

        Args:
            challenge (str): The challenge to change state
        """
    def makehidden(self, challenge):
        """
        Makes a Challenge Hidden

        Args:
            challenge (str): The challenge to change state
        """

    def processrequirements(self, challenge,challenge_id,data):
        """
        Use a PATCH request to modify the Challenge Requirements
        """
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
        """
        deletes all hints from ctfd
        HARD MODE: ON
        """
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
   