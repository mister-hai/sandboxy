import requests
loginurl = "http://127.0.0.1:8000/login"
#loginurl = "http://127.0.0.1:8000/api/v1/login"
#settingsurl = "http://127.0.0.1:8000/settings"
tokensurl = "http://127.0.0.1:8000/api/v1/tokens"
adminchallengesendpoint = 'http://127.0.0.1:8000/api/v1/challenges?view=admin'
challengesurl = "http://127.0.0.1:8000/api/v1/challenges"
useragent = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:28.0) Gecko/20100101  Firefox/28.0'}
authpayload = {
	"name": str,
	"password": str,
	"_submit": "Submit",
	"nonce": str
}
# start session
apisession = requests.Session()
apisession.headers.update(useragent)
apiresponse = apisession.get(url=loginurl, allow_redirects=False)
# set auth fields
authpayload['name'] = "root"
authpayload['password'] ="root"
authpayload['nonce'] = apiresponse.text.split("csrfNonce': \"")[1].split('"')[0]
apiresponse = apisession.post(url=loginurl,data = authpayload)#,allow_redirects=False)
# grab nonce
nonce = apiresponse.text.split("csrfNonce': \"")[1].split('"')[0]
print("============\nNonce: "+ nonce + "\n===============")
# get token URL
#apiresponse = apisession.post(url=settingsurl,json={},headers ={"CSRF-Token": nonce})
#authtoken = apiresponse.json()["data"]["value"]

# get list of challenges
apiresponse = apisession.get(adminchallengesendpoint,json=True)
# token endpoint
apisession.get(tokensurl)
authtoken = apiresponse.json()["data"]["value"]
