
# GET /api/v1/challenge
# List of all challenges
    {
        "success": true,
        "data": [
            {
                "id": 3,
                "type": "multiple_choice",
                "name": "Trivia",
                "value": 42,
                "solves": 4,
                "solved_by_me": false,
                "category": "Multiple Choice",
                "tags": [],
                "template": "/plugins/multiple_choice/assets/view.html",
                "script": "/plugins/multiple_choice/assets/view.js"
            }
        ]
    }

# AUTH TO SERVER
# POST /api/v1/token
    authpayload = {
        "name": str,
        "password": str,
        "_submit": "Submit",
        "nonce": str
    }

# STEP 1
## POST /api/v1/challenges HTTP/1.1

    Creates the initial challenge entry

    challengetemplate = {
        "name": 'command line test',
        "category": 'test',
        "value": "500",
        'description':"A test of uploading via API CLI",
        "state":"hidden",
        "type": 'standard',
    }


# STEP 2
## POST /api/v1/flags HTTP/1.1
    
    flagstemplate = {
        "challenge_id":self.newchallengeID,
        "content":r'''test{testflag}''',
        "type":"static",
        "data":""
    }

# STEP 3
## PATCH /api/v1/challenges/1 HTTP/1.1
    
    {"state":"visible"}

# RETURNS 
## HTTP/1.1 200 OK

    Sets challenge to visible and returns server data on challenge entry?
    new_challenge_id = apiresponse.json()["data"]["id"]


# RETURNS 
## HTTP/1.1 200 OK

    {
        "success": 'true',
        "data": {
            "id": 1, 
            "name": "test",
            "value": 500,
            "description": "test 1",
            "category": "test",
            "state": "visible",
            "max_attempts": 0,
            "type": "standard",
            "type_data": {
                "id": "standard",
                "name": "standard",
                "templates": {
                    "create": "/plugins/challenges/assets/create.html", 
                    "update": "/plugins/challenges/assets/update.html",
                    "view": "/plugins/challenges/assets/view.html"
                    }, 
                "scripts": {
                    "create": "/plugins/challenges/assets/create.js", 
                    "update": "/plugins/challenges/assets/update.js", 
                    "view": "/plugins/challenges/assets/view.js"
                    }
                }
            }
        }
# step 4

## GET /admin/challenges/1 HTTP/1.1
## GET /admin/challenges/1 HTTP/1.1
## GET /api/v1/flags/types HTTP/1.1
## GET /api/v1/challenges/1/tags HTTP/1.1
## GET /api/v1/challenges?view=admin HTTP/1.1
## GET /api/v1/challenges/1/requirements HTTP/1.1

# HTTP/1.1 200 OK
    
    {"success": true, "data": [{"data": "", "challenge": 1, "id": 1, "content": "test{thisisatest}", "challenge_id": 1, "type": "static"}]}

# step 5

## GET /api/v1/challenges/1/files HTTP/1.1
## GET /api/v1/challenges/1/hints HTTP/1.1
## HTTP/1.1 200 OK