import requests
loginurl = "https://demo.ctfd.io/login"
#loginurl = "http://127.0.0.1:8000/api/v1/login"
settingsurl = "https://demo.ctfd.io/settings"
challengesurl = "https://demo.ctfd.io/api/v1/challenges"
useragent = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:28.0) Gecko/20100101  Firefox/28.0'}
authpayload = {
	"name": str,
	"password": str,
	"_submit": "Submit",
	"nonce": str
}
apisession = requests.Session()
apisession.headers.update(useragent)
apiresponse = apisession.get(url=loginurl, allow_redirects=False)
# set auth fields
authpayload['name'] = "admin"
authpayload['password'] ="password"
authpayload['nonce'] = apiresponse.text.split("csrfNonce': \"")[1].split('"')[0]
apiresponse = apisession.post(url=loginurl,data = authpayload)#,allow_redirects=False)
#get settings page
apiresponse = apisession.get(url=settingsurl)
# grab nonce
nonce = apiresponse.text.split("csrfNonce': \"")[1].split('"')[0]
# get token
apiresponse = apisession.post(url=settingsurl,json={},headers ={"CSRF-Token": nonce})
authtoken = apiresponse.json()["data"]["value"]