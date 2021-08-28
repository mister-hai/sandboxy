import requests
from requests import session
from urllib import urljoin

class APISession(Session):
    '''
    Represents a connection to the CTFd API
    '''
    def __init__(self, prefix_url:str, authtoken:str, *args, **kwargs):
        super(APISession, self).__init__(*args, **kwargs)
        # Strip out ending slashes and append a singular one so we generate
        # clean base URLs for both main deployments and subdir deployments
        self.prefix_url = prefix_url.rstrip("/") + "/"
        self.AUTHTOKEN = str

    def request(self, method, url, *args, **kwargs):
        # Strip out the preceding / so that urljoin creates the right url
        # considering the appended / on the prefix_url
        url = urljoin(self.prefix_url, url.lstrip("/"))
        return super(APISession, self).request(method, url, *args, **kwargs)
    
    def uploadfiles(self,challenge,challenge_id,data):
        # Delete existing files
        all_current_files =self.get(f"/api/v1/files?type=challenge", json=data).json()["data"]
        for f in all_current_files:
            for used_file in original_challenge["files"]:
                if f["location"] in used_file:
                    file_id = f["id"]
                    r =self.delete(f"/api/v1/files/{file_id}", json=True)
                    r.raise_for_status()
        files = []
        for f in challenge["files"]:
            file_path = Path(challenge.directory, f)
            if file_path.exists():
                file_object = ("file", file_path.open(mode="rb"))
                files.append(file_object)
            else:
                click.secho(f"File {file_path} was not found", fg="red")
                raise Exception(f"File {file_path} was not found")
        data = {"challenge_id": challenge_id, "type": "challenge"}
    # Sp    ecifically use data= here instead of json= to send multipart/form-data
        r =self.post(f"/api/v1/files", files=files, data=data)
        r.raise_for_status()
        
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
            response = self.post(f"/api/v1/topics",json={"value": topic,"type": "challenge","challenge_id": challenge_id,},)
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