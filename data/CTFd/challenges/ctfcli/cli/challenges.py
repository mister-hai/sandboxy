import os, re
import subprocess
import git, click, yaml
from pathlib import Path
from urllib.parse import urlparse
from cookiecutter.main import cookiecutter

from utils.challenge import (
    create_challenge,
    lint_challenge,
    load_challenge,
    load_installed_challenges,
    sync_challenge,
)

from utils.deploy import DEPLOY_HANDLERS
from utils.spec import CHALLENGE_SPEC_DOCS, blank_challenge_spec
from utils.templates import get_template_dir
from utils.git import get_git_repo_head_branch


###############################################################################
#  CTFCLI HANDLING CLASS
###############################################################################
class ChallengeCategory():
    '''
    use getattr(),setattr() to add/query Challenge Entries
    this is used for keeping track internally

    ChallengeCategory:
        represents a folder in the PROJECTDIRECTORY/data/CTFd/challenges/ dir
      ChallengeEntry:
        represents a challenge.yaml
        name: thing
      ChallengeEntry:
        represents a challenge.yaml
        name: thing
      ChallengeEntry:
        represents a challenge.yaml
        name: thing

    '''
    def __init__(self,name):
        self.name = name
        self.testchallenge = setattr(self,ChallengeEntry("test"))

class Yaml(dict):
    '''
    Represents a challange.yml
    Give Path to challenge.yaml
    '''
    def __init__(self,data, filepath):
        #set the base values
        self.type = str
        #get path of file
        self.filepath = Path(filepath)
        #set working dir of file
        self.directory = self.filepath.parent
        #if its a kubernetes config
        if self.filepath.endswith(".yaml"):
            redprint("[!] File is .yaml! Presuming to be kubernetes config!")
            self.type = "kubernetes"
        else:
            greenprint("[+] Challenge File presumed (.yml)")
            try:
                #open the yml file
                with open(filepath) as f:
                    filedata = yaml.safe_load(f.read(), filepath=filepath)
                    #assign data to self
                    #previous
                    #super().__init__(filedata)
                    setattr(self,"data",filedata)
            except FileNotFoundError:
                print("No challenge.yml was found in {}".format(filepath))

        

class ChallengeEntry():
    '''
    Represents the challenge as exists in the folder for that specific challenge
    '''
    def __init__(self,filepath):
        #get a representation of the challenge.yaml file
        self.challengeyaml = Yaml(filepath=filepath)
        # name of the challenge
        self.name = self.challengeyaml

class ChallengeFolder():
    '''
    Represents the Challenge folder
    '''
    def __init__(self, templatesdir):
        pass
    def load_challenge(path):
        try:
            with open(path) as f:
                return Yaml(data=yaml.safe_load(f.read()), file_path=path)
        except FileNotFoundError:
            click.secho(f"No challenge.yml was found in {path}", fg="red")
            return
    def install(self, challenge:str, force=False, ignore=()):
        '''
        Installs a challenge from a folder
        '''
        challenge = load_challenge(path)
        print(f'Loaded {challenge["name"]}', fg="yellow")
        installed_challenges = load_installed_challenges()
        for chall in installed_challenges:
            if c["name"] == challenge["name"]:
                yellowboldprint("Already found existing challenge with same name \
                    ({}). Perhaps you meant sync instead of install?".format(challenge['name']))
                if force is True:
                    yellowboldprint("Ignoring existing challenge because of --force")
                else:
                        break
            else:  # If we don't break because of duplicated challenge names
                print(f'Installing {challenge["name"]}', fg="yellow")
                create_challenge(challenge=challenge, ignore=ignore)
                print("Success!", fg="green")

    def sync(self, challenge=None, ignore=()):
        if challenge is None:
            # Get all challenges if not specifying a challenge
            config = load_config()
            challenges = dict(config["challenges"]).keys()
        else:
            challenges = [challenge]

        if isinstance(ignore, str):
            ignore = (ignore,)

        for challenge in challenges:
            path = Path(challenge)

            if path.name.endswith(".yml") is False:
                path = path / "challenge.yml"

            print("Found {path}")
            challenge = load_challenge(path)
            print(f'Loaded {challenge["name"]}', fg="yellow")

            installed_challenges = load_installed_challenges()
            for c in installed_challenges:
                if c["name"] == challenge["name"]:
                    break
            else:
                print(
                    f'Couldn\'t find existing challenge {c["name"]}. Perhaps you meant install instead of sync?',
                    fg="red",
                )
                continue  # Go to the next challenge in the overall list

            print(f'Syncing {challenge["name"]}', fg="yellow")
            sync_challenge(challenge=challenge, ignore=ignore)
            print("Success!", fg="green")

    def update(self, challenge=None):
        config = load_config()
        challenges = dict(config["challenges"])
        for folder, url in challenges.items():
            if challenge and challenge != folder:
                continue
            if url.endswith(".git"):
                click.echo(f"Pulling latest {url} to {folder}")
                head_branch = get_git_repo_head_branch(url)
                subprocess.call(
                    [
                        "git",
                        "subtree",
                        "pull",
                        "--prefix",
                        folder,
                        url,
                        head_branch,
                        "--squash",
                    ],
                    cwd=get_project_path(),
                )
                subprocess.call(["git", "mergetool"], cwd=folder)
                subprocess.call(["git", "clean", "-f"], cwd=folder)
                subprocess.call(["git", "commit", "--no-edit"], cwd=folder)
            else:
                click.echo(f"Skipping {url} - {folder}")

    def finalize(self, challenge=None):
        if challenge is None:
            challenge = os.getcwd()

        path = Path(challenge)
        spec = blank_challenge_spec()
        for k in spec:
            q = CHALLENGE_SPEC_DOCS.get(k)
            fields = q._asdict()

            ask = False
            required = fields.pop("required", False)
            if required is False:
                try:
                    ask = click.confirm(f"Would you like to add the {k} field?")
                    if ask is False:
                        continue
                except click.Abort:
                    click.echo("\n")
                    continue

            if ask is True:
                fields["text"] = "\t" + fields["text"]

            multiple = fields.pop("multiple", False)
            if multiple:
                fields["text"] += " (Ctrl-C to continue)"
                spec[k] = []
                try:
                    while True:
                        r = click.prompt(**fields)
                        spec[k].append(r)
                except click.Abort:
                    click.echo("\n")
            else:
                try:
                    r = click.prompt(**fields)
                    spec[k] = r
                except click.Abort:
                    click.echo("\n")

        with open(path / "challenge.yml", "w+") as f:
            yaml.dump(spec, stream=f, default_flow_style=False, sort_keys=False)

        print("challenge.yml written to", path / "challenge.yml")

    def lint(self, challenge=None):
        if challenge is None:
            challenge = os.getcwd()

        path = Path(challenge)

        if path.name.endswith(".yml") is False:
            path = path / "challenge.yml"

        lint_challenge(path)

    def deploy(self, challenge, host=None):
        if challenge is None:
            challenge = os.getcwd()

        path = Path(challenge)

        if path.name.endswith(".yml") is False:
            path = path / "challenge.yml"

        challenge = load_challenge(path)
        image = challenge.get("image")
        target_host = host or challenge.get("host") or input("Target host URI: ")
        if image is None:
            print(
                "This challenge can't be deployed because it doesn't have an associated image",
                fg="red",
            )
            return
        if bool(target_host) is False:
            print(
                "This challenge can't be deployed because there is no target host to deploy to",
                fg="red",
            )
            return
        url = urlparse(target_host)

        if bool(url.netloc) is False:
            print("Provided host has no URI scheme. Provide a URI scheme like ssh:// or registry://")
            return

        status, domain, port = DEPLOY_HANDLERS[url.scheme](challenge=challenge, host=target_host)
        if status:
            greenprint("[+] Challenge deployed at {}:{}".format(domain,port)
        else:
            redprint("[-] ERROR: deployment failed! Check the logfile!")


