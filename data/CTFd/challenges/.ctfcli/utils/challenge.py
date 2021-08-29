from apicalls import APISession
from pathlib import Path
import subprocess
from utils import errorlogger,yellowboldprint,greenprint

import click
import yaml
from Yaml import Yaml

class Challenge(): #folder
    '''
    Maps to the command:
    user@server$> ctfcli challenge

    Represents the Challenge folder
    not loaded into fire
    '''
    def __init__(self, templatesdir):
        pass

    def load_challenge(self,path):
        try:
            with open(path) as f:
                return Yaml(data=yaml.safe_load(f.read()), file_path=path)
        except FileNotFoundError:
            errorlogger("No challenge.yml was found in {}".format(path))
            return

    def install(self, challenge:str, force=False, ignore=()):
        '''
        Installs a challenge from a folder
        takes a path to a challenge.yml
        '''
        challenge = self.load_challenge(challenge)
        print(f'Loaded {challenge["name"]}', fg="yellow")
        installed_challenges = loadinstalledchallenges()
        for chall in installed_challenges:
            if chall["name"] == challenge["name"]:
                yellowboldprint("Already found existing challenge with same name \
                    ({}). Perhaps you meant sync instead of install?".format(challenge['name']))
                if force is True:
                    yellowboldprint("Ignoring existing challenge because of --force")
                else:
                        break
            else:  # If we don't break because of duplicated challenge names
                print(f'Installing {challenge["name"]}', fg="yellow")
                GitOperations.addchallenge(challenge=challenge, ignore=ignore)
                print("Success!", fg="green")

    def sync(self, challenge=None, ignore=()):
            challenge = self.load_challenge(challenge)
            greenprint('Loaded {}'.format(challenge["name"]))

            #get list of all challenges
            installed_challenges = load_installed_challenges()
            for c in installed_challenges:
                if c["name"] == challenge["name"]:
                    break
            else:
                print(f'Couldn\'t find existing challenge {c["name"]}. Perhaps you meant install instead of sync?')
                continue  # Go to the next challenge in the overall list

            print(f'Syncing {challenge["name"]}', fg="yellow")
            sync_challenge(challenge=challenge, ignore=ignore)
                def syncchallenge(self,challenge:dict):
        '''
        Adds a challenge
            Must be in its own folder, in a category that has been indexed
        
        This command is to be run on single cchallenge folders
        This command is called RECURSIVELY by other code, referece its input and output
        '''
        greenprint(f"Syncing challenge: {challenge}")
        getchallengebyname(challenge)

        #TOTO SET CHALLENGE ID
        challenge_id = str
        try:
            #assign data fields to json
            challengevalue       = int(challenge["value"]) if challenge["value"] else challenge["value"],challenge.get("extra", {})
            challengetype        = challenge.get("type", "standard")
            challengedescription = challenge["description"]
            challengecategory    = challenge["category"]
            challengename        = challenge["name"]
            challengeauthor      = challenge["author"]
            data = {
                "name":         challengename,
                "category":     challengecategory,
                "description":  challengedescription,
                "type":         challengetype,
                "value" :       challengevalue,
                "author" :      challengeauthor
                }
            
            #make API call
            apicall = APISession(prefix_url=self.CTFD_URL)
            apicall.headers.update({"Authorization": "Token {}".format(apicall.AUTHTOKEN)})
            apisess = apicall.get("/api/v1/challenges/{}".format(challenge_id), json=data).json()["data"]
            response = apisess.patch(f"/api/v1/challenges/{challenge_id}", json=data)
            response.raise_for_status()
            
            # Create new flags
            if challenge.get("flags"):
                apicall.processflags(challenge,challenge_id,data)
 
            # Update topics
            if challenge.get("topics"):
                apicall.processtopics(challenge,challenge_id,data)

            # Update tags
            if challenge.get("tags"):
                apicall.processtopics(challenge,challenge_id,data)

            # Upload files
            if challenge.get("files"):
                apicall.uploadfiles(challenge,challenge_id,data)

            # Create hints
            if challenge.get("hints"):
                # Delete existing hints
                current_hints = s.get(f"/api/v1/hints", json=data).json()["data"]
                for hint in current_hints:
                    if hint["challenge_id"] == challenge_id:
                        hint_id = hint["id"]
                        r = s.delete(f"/api/v1/hints/{hint_id}", json=True)
                        r.raise_for_status()
                for hint in challenge["hints"]:
                    if type(hint) == str:
                        data = {"content": hint, "cost": 0, "challenge_id": challenge_id}
                    else:
                        data = {
                            "content": hint["content"],
                            "cost": hint["cost"],
                            "challenge_id": challenge_id,
                        }
                    r = s.post(f"/api/v1/hints", json=data)
                    r.raise_for_status()
            # Update requirements
            if challenge.get("requirements") and "requirements" not in ignore:
                installed_challenges = load_installed_challenges()
                required_challenges = []
                for r in challenge["requirements"]:
                    if type(r) == str:
                        for c in installed_challenges:
                            if c["name"] == r:
                                required_challenges.append(c["id"])
                    elif type(r) == int:
                        required_challenges.append(r)
                required_challenges = list(set(required_challenges))
                data = {"requirements": {"prerequisites": required_challenges}}
                r = s.patch(f"/api/v1/challenges/{challenge_id}", json=data)
                r.raise_for_status()
            # Unhide challenge depending upon the value of "state" in spec
            if "state" not in ignore:
                data = {"state": "visible"}
                if challenge.get("state"):
                    if challenge["state"] in ["hidden", "visible"]:
                        data["state"] = challenge["state"]
                r = s.patch(f"/api/v1/challenges/{challenge_id}", json=data)
                r.raise_for_status()
        except Exception:
            errorlogger("[-] Failure, INPUT: {}".format(challenge))


def sync_challenge(challenge, ignore=[]):
    data = {
        "name": challenge["name"],
        "category": challenge["category"],
        "description": challenge["description"],
        "type": challenge.get("type", "standard"),
        "value": int(challenge["value"]) if challenge["value"] else challenge["value"],
        **challenge.get("extra", {}),
    }

    # Some challenge types (e.g. dynamic) override value.
    # We can't send it to CTFd because we don't know the current value
    if challenge["value"] is None:
        del challenge["value"]

    if challenge.get("attempts") and "attempts" not in ignore:
        data["max_attempts"] = challenge.get("attempts")

    if challenge.get("connection_info") and "connection_info" not in ignore:
        data["connection_info"] = challenge.get("connection_info")

    data["state"] = "hidden"

    installed_challenges = load_installed_challenges()
    for c in installed_challenges:
        if c["name"] == challenge["name"]:
            challenge_id = c["id"]
            break
    else:
        return
    session = APISession()
    original_challenge =session.get(f"/api/v1/challenges/{challenge_id}", json=data).json()["data"]
    r =session.patch(f"/api/v1/challenges/{challenge_id}", json=data)

    # Create new flags
    if challenge.get("flags") and "flags" not in ignore:
        # Delete existing flags
        current_flags =session.get(f"/api/v1/flags", json=data).json()["data"]
        for flag in current_flags:
            if flag["challenge_id"] == challenge_id:
                flag_id = flag["id"]
                r =session.delete(f"/api/v1/flags/{flag_id}", json=True)
                r.raise_for_status()
        for flag in challenge["flags"]:
            if type(flag) == str:
                data = {"content": flag, "type": "static", "challenge_id": challenge_id}
                r =session.post(f"/api/v1/flags", json=data)
                r.raise_for_status()
            elif type(flag) == dict:
                flag["challenge_id"] = challenge_id
                r =session.post(f"/api/v1/flags", json=flag)
                r.raise_for_status()

    # Update topics
    if challenge.get("topics") and "topics" not in ignore:
        # Delete existing challenge topics
        current_topics =session.get(f"/api/v1/challenges/{challenge_id}/topics", json="").json()["data"]
        for topic in current_topics:
            topic_id = topic["id"]
            r =session.delete(f"/api/v1/topics?type=challenge&target_id={topic_id}", json=True)
            r.raise_for_status()
        # Add new challenge topics
        for topic in challenge["topics"]:
            r =session.post(f"/api/v1/topics",
                json={
                    "value": topic,
                    "type": "challenge",
                    "challenge_id": challenge_id,
                },)
            r.raise_for_status()

    # Update tags
    if challenge.get("tags") and "tags" not in ignore:
        # Delete existing tags
        current_tags =session.get(f"/api/v1/tags", json=data).json()["data"]
        for tag in current_tags:
            if tag["challenge_id"] == challenge_id:
                tag_id = tag["id"]
                r =session.delete(f"/api/v1/tags/{tag_id}", json=True)
                r.raise_for_status()
        for tag in challenge["tags"]:
            r =session.post(
                f"/api/v1/tags", json={"challenge_id": challenge_id, "value": tag}
            )
            r.raise_for_status()

    # Upload files
    if challenge.get("files") and "files" not in ignore:
        # Delete existing files
        all_current_files =session.get(f"/api/v1/files?type=challenge", json=data).json()[
            "data"
        ]
        for f in all_current_files:
            for used_file in original_challenge["files"]:
                if f["location"] in used_file:
                    file_id = f["id"]
                    r =session.delete(f"/api/v1/files/{file_id}", json=True)
                    r.raise_for_status()
        files = []
        for f in challenge["files"]:
            file_path = Path(challenge.directory, f)
            if file_path.exists():
                file_object = ("file", file_path.open(mode="rb"))
                files.append(file_object)
            else:
                click.secho(f"File {file_path} was not found", fg="red")
                raise Exception(f"File {file_path} was not found")

        data = {"challenge_id": challenge_id, "type": "challenge"}
        # Specifically use data= here instead of json= to send multipart/form-data
        r =session.post(f"/api/v1/files", files=files, data=data)
        r.raise_for_status()

    # Create hints
    if challenge.get("hints") and "hints" not in ignore:
        # Delete existing hints
        current_hints =session.get(f"/api/v1/hints", json=data).json()["data"]
        for hint in current_hints:
            if hint["challenge_id"] == challenge_id:
                hint_id = hint["id"]
                r =session.delete(f"/api/v1/hints/{hint_id}", json=True)
                r.raise_for_status()

        for hint in challenge["hints"]:
            if type(hint) == str:
                data = {"content": hint, "cost": 0, "challenge_id": challenge_id}
            else:
                data = {
                    "content": hint["content"],
                    "cost": hint["cost"],
                    "challenge_id": challenge_id,
                }

            r =session.post(f"/api/v1/hints", json=data)
            r.raise_for_status()

    # Update requirements
    if challenge.get("requirements") and "requirements" not in ignore:
        installed_challenges = load_installed_challenges()
        required_challenges = []
        for r in challenge["requirements"]:
            if type(r) == str:
                for c in installed_challenges:
                    if c["name"] == r:
                        required_challenges.append(c["id"])
            elif type(r) == int:
                required_challenges.append(r)

        required_challenges = list(set(required_challenges))
        data = {"requirements": {"prerequisites": required_challenges}}
        r =session.patch(f"/api/v1/challenges/{challenge_id}", json=data)
        r.raise_for_status()

    # Unhide challenge depending upon the value of "state" in spec
    if "state" not in ignore:
        data = {"state": "visible"}
        if challenge.get("state"):
            if challenge["state"] in ["hidden", "visible"]:
                data["state"] = challenge["state"]

        r =session.patch(f"/api/v1/challenges/{challenge_id}", json=data)
        r.raise_for_status()


def create_challenge(challenge, ignore=[]):
    data = {
        "name": challenge["name"],
        "category": challenge["category"],
        "description": challenge["description"],
        "type": challenge.get("type", "standard"),
        "value": int(challenge["value"]) if challenge["value"] else challenge["value"],
        **challenge.get("extra", {}),
    }

    # Some challenge types (e.g. dynamic) override value.
    # We can't send it to CTFd because we don't know the current value
    if challenge["value"] is None:
        del challenge["value"]

    if challenge.get("attempts") and "attempts" not in ignore:
        data["max_attempts"] = challenge.get("attempts")

    if challenge.get("connection_info") and "connection_info" not in ignore:
        data["connection_info"] = challenge.get("connection_info")

    s = generate_session()

    r =session.post("/api/v1/challenges", json=data)
    r.raise_for_status()

    challenge_data = r.json()
    challenge_id = challenge_data["data"]["id"]

    # Create flags
    if challenge.get("flags") and "flags" not in ignore:
        for flag in challenge["flags"]:
            if type(flag) == str:
                data = {"content": flag, "type": "static", "challenge_id": challenge_id}
                r =session.post(f"/api/v1/flags", json=data)
                r.raise_for_status()
            elif type(flag) == dict:
                flag["challenge"] = challenge_id
                r =session.post(f"/api/v1/flags", json=flag)
                r.raise_for_status()

    # Create topics
    if challenge.get("topics") and "topics" not in ignore:
        for topic in challenge["topics"]:
            r =session.post(
                f"/api/v1/topics",
                json={
                    "value": topic,
                    "type": "challenge",
                    "challenge_id": challenge_id,
                },
            )
            r.raise_for_status()

    # Create tags
    if challenge.get("tags") and "tags" not in ignore:
        for tag in challenge["tags"]:
            r =session.post(
                f"/api/v1/tags", json={"challenge_id": challenge_id, "value": tag}
            )
            r.raise_for_status()

    # Upload files
    if challenge.get("files") and "files" not in ignore:
        files = []
        for f in challenge["files"]:
            file_path = Path(challenge.directory, f)
            if file_path.exists():
                file_object = ("file", file_path.open(mode="rb"))
                files.append(file_object)
            else:
                click.secho(f"File {file_path} was not found", fg="red")
                raise Exception(f"File {file_path} was not found")

        data = {"challenge_id": challenge_id, "type": "challenge"}
        # Specifically use data= here instead of json= to send multipart/form-data
        r =session.post(f"/api/v1/files", files=files, data=data)
        r.raise_for_status()

    # Add hints
    if challenge.get("hints") and "hints" not in ignore:
        for hint in challenge["hints"]:
            if type(hint) == str:
                data = {"content": hint, "cost": 0, "challenge_id": challenge_id}
            else:
                data = {
                    "content": hint["content"],
                    "cost": hint["cost"],
                    "challenge_id": challenge_id,
                }

            r =session.post(f"/api/v1/hints", json=data)
            r.raise_for_status()

    # Add requirements
    if challenge.get("requirements") and "requirements" not in ignore:
        installed_challenges = load_installed_challenges()
        required_challenges = []
        for r in challenge["requirements"]:
            if type(r) == str:
                for c in installed_challenges:
                    if c["name"] == r:
                        required_challenges.append(c["id"])
            elif type(r) == int:
                required_challenges.append(r)

        required_challenges = list(set(required_challenges))
        data = {"requirements": {"prerequisites": required_challenges}}
        r =session.patch(f"/api/v1/challenges/{challenge_id}", json=data)
        r.raise_for_status()

    # Set challenge state
    if challenge.get("state") and "state" not in ignore:
        data = {"state": "hidden"}
        if challenge["state"] in ["hidden", "visible"]:
            data["state"] = challenge["state"]

        r =session.patch(f"/api/v1/challenges/{challenge_id}", json=data)
        r.raise_for_status()


def lint_challenge(path):
    try:
        challenge = load_challenge(path)
    except yaml.YAMLError as e:
        click.secho(f"Error parsing challenge.yml: {e}", fg="red")
        exit(1)

    required_fields = ["name", "author", "category", "description", "value"]
    errors = []
    for field in required_fields:
        if field == "value" and challenge.get("type") == "dynamic":
            pass
        else:
            if challenge.get(field) is None:
                errors.append(field)

    if len(errors) > 0:
        print("Missing fields: ", ", ".join(errors))
        exit(1)

    # Check that the image field and Dockerfile match
    if (Path(path).parent / "Dockerfile").is_file() and challenge.get("image") != ".":
        print("Dockerfile exists but image field does not point to it")
        exit(1)

    # Check that Dockerfile exists and is EXPOSE'ing a port
    if challenge.get("image") == ".":
        try:
            dockerfile = (Path(path).parent / "Dockerfile").open().read()
        except FileNotFoundError:
            print("Dockerfile specified in 'image' field but no Dockerfile found")
            exit(1)

        if "EXPOSE" not in dockerfile:
            print("Dockerfile missing EXPOSE")
            exit(1)

        # Check Dockerfile with hadolint
        proc = subprocess.run(
            ["docker", "run", "--rm", "-i", "hadolint/hadolint"],
            input=dockerfile.encode(),
        )
        if proc.returncode != 0:
            print("Hadolint found Dockerfile lint issues, please resolve")
            exit(1)

    # Check that all files exists
    files = challenge.get("files", [])
    errored = False
    for f in files:
        fpath = Path(path).parent / f
        if fpath.is_file() is False:
            print(f"File {f} specified but not found at {fpath.absolute()}")
            errored = True
    if errored:
        exit(1)

    exit(0)
