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
