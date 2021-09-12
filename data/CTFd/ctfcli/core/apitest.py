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
emptychallengesresponse = {"success": 'true', "data": []}
testchallengesresponse = {
			"success": 'true',
			"data": [
				{
					"id": 1,
					"type": "standard",
					"name": "test",
					"value": 500,
					"solves": 0,
					"solved_by_me": true,
					"category": "test",
					"tags": [],
					"template": "/plugins/challenges/assets/view.html",
					"script": "/plugins/challenges/assets/view.js"
				}, 
				{
					"id": 2,
					"type": "dynamic",
					"name": "dynamic test",
					"value": 500,
					"solves": 0,
					"solved_by_me": true,
					"category": "test",
					"tags": [],
					"template": "/plugins/dynamic_challenges/assets/view.html",
					"script": "/plugins/dynamic_challenges/assets/view.js"
				}
			]
		}
# token endpoint
apisession.get(tokensurl)
authtoken = apiresponse.json()["data"]["value"]
tokenresponse = {
				"success": true, 
				"data": {
						"created": "2021-09-12T08:59:52.421062+00:00", 
						"value": "e2c1cb51859e5d7afad6c2cd82757277077a564166d360b48cafd5fcc1e4e015", 
						"type": "user",
						"id": 1,
						"expiration":"2021-10-12T08:59:52.421073+00:00",
						"user_id": 1
						}
				}
