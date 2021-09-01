import json
from pathlib import Path
from requests import Session
from utils import errorlogger,blueprint,yellowboldprint,redprint
from ctfdrepo import SandboxyCTFdRepository

class APIHandler():
    def __init__(self, ctfdurl,authtoken):
        self.ctfdurl = ctfdurl
        self.authtoken = authtoken


class APISession(Session):
    def __init__(self, *args, **kwargs):
        """
        Represents a connection to the CTFd API
        """

    #def request(self, method, url, *args, **kwargs):
        # Strip out the preceding / so that urljoin creates the right url
        # considering the appended / on the prefix_url
        #url = urljoin(self.prefix_url, url.lstrip("/"))
        #return super(APISession, self).request(method, url, *args, **kwargs)

    def makegetrequest(self, jsonpayload:json):
        '''
        Performs a request to the CTFd server API
        '''
        # auth to server
        self.headers.update({"Authorization": "Token {}".format(self.AUTHTOKEN)})
        # check for challenge install
        apisess = self.get("/api/v1/challenges/{}".format(self.id), json=jsonpayload).json()["data"]
        # use requests.patch() to modify the value of a specific field on an existing APIcall.
        # why are they patching the challenge ID?
        response = apisess.patch(f"/api/v1/challenges/{self.id}", json=jsonpayload)
        response.raise_for_status()


    def uploadfiles(self,challenge,challenge_id,data):
        """
        uploads files to the ctfd server
        SAW ELSEWHERE IT HAD THIS
## Upload a file to a challenge.  You need to use a nonce from the admin page of the challenge you're editing.
nonce=$(curl -s http://127.0.0.1:8000/admin/challenges/1 -b cookie | grep nonce | cut -d'"' -f2)
curl -X POST "http://127.0.0.1:8000/api/v1/files" -b cookie  \
-F "file=@some-local-file.png" \
-F "nonce=$nonce" \
-F "challenge=1" \
-F "type=challenge"
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

    def processtopics(self,data):
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

    def was_there_was_an_error(self, responsecode):
        """ Returns False if no error"""
        # server side error]
        set1 = [404,504,503,500]
        set2 = [400,405,501]
        set3 = [500]
        if responsecode in set1 :
            errorlogger("[-] Server side error - No Resource Available in REST response - Error Code {}".format(responsecode))
            return True # "[-] Server side error - No resource Available in REST response"
        if responsecode in set2:
            errorlogger("[-] User error in Request - Error Code {}".format(responsecode))
            return True # "[-] User error in Image Request"
        if responsecode in set3:
            #unknown error
            errorlogger("[-] Unknown Server Error - No Resource Available in REST response - Error Code {}".format(responsecode)) 
            return True # "[-] Unknown Server Error - No Image Available in REST response"
        # no error!
        if responsecode == 200:
            return False