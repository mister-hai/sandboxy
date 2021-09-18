#wat

def authtemplate():
    return {
            "name": str,
            "password": str,
            "_submit": "Submit",
            "nonce": str
        }

def valuetemplate(): 
    return {
            "value": int,
            }

def challengetemplate():
    return {
            "name": str,
            "category": str,
            "value": int,
            'description':str,
            "state":str,
            "type": str,
            #"tags": list,#[],
            #'flags':r'''test{testflag}'''
            #"solves": int,#4,
            #"solved_by_me": str,#'false',
            #"template": str,#"/plugins/multiple_choice/assets/view.html",
            #"script": str#"/plugins/multiple_choice/assets/view.js"
    }

def dynamicchallengetemplate():
    return {
            "name":"dynamic test",
            "category":str,
            "description":str,
            "initial":str,
            "decay":str,
            "minimum":str,
            "state":"hidden",
            "type":"dynamic"
            }

def topictemplate():
    return {
                    "value": str,
                    "type": str,#"challenge",
                    "challenge_id": int,
                }
def hintstemplate():
    return {
            "content": str,
            "cost": int,
            "challenge_id": int,
                }
def flagstemplate():
    return {

        }
        
def tokentemplate():
    # this is returned from a token request
    return {
			"success": str,#'true', 
			"data": {
				"created": str,#"2021-09-12T08:59:52.421062+00:00", 
				"value": str,#"e2c1cb51859e5d7afad6c2cd82757277077a564166d360b48cafd5fcc1e4e015", 
				"type": str,#"user",
				"id": int,#1,
				"expiration":str,#"2021-10-12T08:59:52.421073+00:00",
				"user_id": int#1
				}
			}
def authtemplate():
    # template for authentication packet
    return {
	        "name": str,
	        "password": str,
	        "_submit": "Submit",
	        "nonce": str #"84e85c763320742797291198b9d52cf6c82d89f120e2551eb7bf951d44663977"
        }
