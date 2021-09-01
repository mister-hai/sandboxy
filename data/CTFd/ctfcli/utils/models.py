
def usertemplate():
    """
    returns a json template for api calls to
    /api/v1/users
    """
    #USERTEMPLATE = {
    return {
            "name":"foobar",
            "email":"foo@bar.com",
            "password":"123",
            "type":"user",
            "verified":"false",
            "hidden":"false",
            "banned":"false"
            }

def challengetemplate():
    """
    Returns a json template for api calls to 
    /api/v1/challenge
    """
    #CHALLENGETEMPLATE = {
    return {
            "success": "true",
            "data": [ {
                        "id": 1,
                        "type": "standard",
                        "name": "The Lost Park",
                        "value": 50,
                        "solves": 3,
                        "solved_by_me": "false",
                        "category": "Forensics",
                        "tags": [],
                        "template": "/plugins/challenges/assets/view.html",
                        "script": "/plugins/challenges/assets/view.js"
                    }]
            }