import requests
loginurl = "http://127.0.0.1:8000/login"
#loginurl = "http://127.0.0.1:8000/api/v1/login"
settingsurl = "http://127.0.0.1:8000/settings#tokens"
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
challengetemplate = {
                "type": 'standard',
                "name": 'command line test',
                "value": 500,
                "category": 'test',
                "tags": 'commandlinetest',
				'description':"A test of uploading via API CLI",
				'flags':r'''test{testflag}'''
}
def getidbyname(apiresponse:requests.Response):
	"""
	get challenge ID to prevent collisions
	"""
	# list of all challenges
	apidict = apiresponse.json()["data"]
	for each in apidict:
		#challengeids = [{k: v} for x in apidict for k, v in x.items()]
		print('NAME: ' + each.get('name'))
		print("ID: " + str(each.get('id')))

# start session
apisession = requests.Session()
apisession.headers.update(useragent)
apiresponse = apisession.get(url=loginurl, allow_redirects=False)
# set auth fields
authpayload['name'] = "root"
authpayload['password'] ="password"
# set initial interaction nonce
nonce = apiresponse.text.split("csrfNonce': \"")[1].split('"')[0]
print("============\nInitial Nonce: "+ nonce + "\n===============")
authpayload['nonce'] = nonce
# send POST to Login URL
apiresponse = apisession.post(url=loginurl,data = authpayload)#,allow_redirects=False)
# grab admin login nonce
nonce = apiresponse.text.split("csrfNonce': \"")[1].split('"')[0]
print("============\nAdmin Nonce: "+ nonce + "\n===============")
# POST to tokensurl to obtain Token
apiresponse = apisession.post(url=tokensurl,json={},headers ={"CSRF-Token": nonce})
# Place token into headers for sessions to interact with WRITE permissions
authtoken = apiresponse.json()["data"]["value"]
apisession.headers.update({"Authorization": "Token {}".format(authtoken)})
# get list of challenges
apiresponse = apisession.get(adminchallengesendpoint,json=True)
getidbyname(apiresponse)
#emptychallengesresponse = {"success": 'true', "data": []}
# create new challenge
apiresponse = apisession.post(url=adminchallengesendpoint, data=challengetemplate,allow_redirects=False)
