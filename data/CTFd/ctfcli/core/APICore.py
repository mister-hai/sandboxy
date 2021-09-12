from requests import Session

class APICore(Session):
    def __cls__(cls):

        cls.routeslist = ["challenges","tags","topics","awards",
        "hints", "flags","submissions","scoreboard",
        "teams","users","statistics","files", "notifications",
        "configs", "pages", "unlocks", "tokens", "comments"]
        cls.challengetemplate = {"data": [
            {
                "id": 3,
                "type": "multiple_choice",
                "name": "Trivia",
                "value": 42,
                "solves": 4,
                "solved_by_me": 'false',
                "category": "Multiple Choice",
                "tags": [],
                "template": "/plugins/multiple_choice/assets/view.html",
                "script": "/plugins/multiple_choice/assets/view.js"
            }]
        }
        cls.flagstemplate = {
            "success": 'true',
            "data": [
                {
                    "content": "test{thisisatest}",
                    "id": 1,
                    "challenge_id": 1,
                    "type": "static",
                    "data": "",
                    "challenge": 1
                }
            ]
        }
        cls.tokentemplate = {
				"success": 'true', 
				"data": {
						"created": "2021-09-12T08:59:52.421062+00:00", 
						"value": "e2c1cb51859e5d7afad6c2cd82757277077a564166d360b48cafd5fcc1e4e015", 
						"type": "user",
						"id": 1,
						"expiration":"2021-10-12T08:59:52.421073+00:00",
						"user_id": 1
						}
				}