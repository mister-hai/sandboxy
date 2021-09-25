import subprocess
import yaml
import subprocess
from pathlib import Path
from ctfcli.utils.utils import errorlogger

class ChallengeTemplate():
    """
    Template to validate challenge.yaml

    Future replacment for the top HALF of the ctfcli.core.challenge.Challenge code
    """

class Linter():
    """
    Class to lint challenge.yaml files to decrease size of Challenge class
    codebase
    """
    def __init__(self,
                kwargs:dict,
                togglevisibility=True):
    
        # the base repo has too few challenges to justify making any invisible
        # right from the get go, so its set to true by default
        self.toggle = togglevisibility
        # BSIDES STUFF ONLY
        # This is the standard metadata for a challenge with a web component.
        # In terms of file structure, please also have the following:
        #
        # - A challenge/ folder with everything needed to create the challenge assets
        # - A distfiles/ folder which contains all files (or symlinks to files) that
        #   will be attached to the challenge
        # - A solution/ folder with a working solution to the challenge (or a README.md
        #   file documenting the solution)
        challengeyamltags = [
                            'version' ,'name', 'scoreboard_name', 
                            'author', 'flag', 'description',
                            'value', 'tags', 'port', 'protocol', 
                            'use_http_loadbalancer','notes','replicas',
                            'environ'
                            ]
        deploymentfields = [
                            'port', 'protocol', 'use_http_loadbalancer',
                            "image","host","connection_info" 
                            ]
        requiredfields = ["name", "category", "description", "value"]#,"author"]
        #Required sections get the "pop()" function 
        # a KeyError will be raised if the key does not exist

        def _processrequired(self,dictfromyaml):
            """
            process required challenge fields from challenge.yaml
            """
            try:
                for tag in requiredfields:
                    setattr(self,tag,kwargs.pop("tag"))
            except Exception:
                errorlogger("[-] Challenge.yaml does not conform to specification, \
                    rejecting. Please check the error log.")

        ['value', "topics","tags","hints","requirements","version"]
        
        
        # lets process flags seperately, just cause people sometimes add an "s"
        try:
            self.flags = kwargs.pop('flags')
        except Exception:
            try:
                self.flags = kwargs.pop('flag')
            except Exception:
                errorlogger('[-] ERROR: No flag in challenge')
                pass
        
        # we should set state to visible unless self.toggle is set to false
        if kwargs.get("state") != None:
            self.state = kwargs.get("state")
        else:
            self.state = "visible"

        if type(kwargs.get('value')) != int:
            raise TypeError
        else:
            self.value = kwargs.pop('value')

        # older versions have "static" as value for "standard"?
        self.typeof = kwargs.pop('type')
        if self.typeof == 'static':
            self.typeof = 'standard'
        # get extra field if exists
        if self.typeof == 'dynamic':
            self.extra = kwargs.pop("extra")


        ################################
        # FILES
        ################################
        self.files = kwargs.get('files')
    CHALLENGE_SPEC_DOCS = {
        "name": "Challenge name or identifier",
        "author": "Your name or handle",
        "category":"Challenge category",
        "description": "Challenge description shown to the user",
        "value": "How many points your challenge should be worth",
        "version":"What version of the challenge specification was used",
        "image": "Docker image used to deploy challenge",
        "type": "Type of challenge",
        "attempts": "How many attempts should the player have",
        "flags": "Flags that mark the challenge as solved",
        "tags":"Tag that denotes a challenge topic",
        "files": "Files to be shared with the user",
        "hints": "Hints to be shared with the user",
        "requirements": "Challenge dependencies that must be solved before this one can be attempted",
    }


    def blank_challenge_spec():
        pwd = Path(__file__)
        spec = pwd.parent.parent / "spec" / "challenge-example.yml"
        with open(spec) as f:
            blank = yaml.safe_load(f)

        for k in blank:
            if k != "version":
                blank[k] = None

        return blank


    def lint_challenge(self, loadedyaml):
        requiredfields = ["name", "author", "category", "description", "value"]
        optionalfields= []
        errors = []
        for field in required_fields:
            if field == "value" and challenge.type == "dynamic":
                pass
            else:
                if challenge.get(field) is None:
                    errors.append(field)
        if len(errors) > 0:
            print("Missing fields: ", ", ".join(errors))
            exit(1)
        # Check that the image field and Dockerfile match
        if (Path(challenge).parent / "Dockerfile").is_file() and challenge.image != ".":
            print("Dockerfile exists but image field does not point to it")
            exit(1)
        # Check that Dockerfile exists and is EXPOSE'ing a port
        if challenge.image == ".":
            try:
                dockerfile = (Path(challenge.path).parent / "Dockerfile").open().read()
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
            fpath = Path(challenge.path).parent / f
            if fpath.is_file() is False:
                print(f"File {f} specified but not found at {fpath.absolute()}")
                errored = True
        if errored:
            exit(1)
        else:
            exit(0)
