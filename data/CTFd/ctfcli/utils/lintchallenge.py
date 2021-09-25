from pathlib import Path
import subprocess
import yaml
import getpass
import subprocess
from pathlib import Path
from collections import namedtuple

allowedfields = []

class ChallengeTemplate():
    """
    Template to validate challenge.yaml

    Future replacment for the top HALF of the ctfcli.core.challenge.Challenge code
    """

Prompt = namedtuple("Prompt", ["text", "type", "default", "required", "multiple"])

CHALLENGE_SPEC_DOCS = {
    "name": Prompt(
        text="Challenge name or identifier",
        type=None,
        default=None,
        required=True,
        multiple=False,
    ),
    "author": Prompt(
        text="Your name or handle",
        type=None,
        default=getpass.getuser(),
        required=True,
        multiple=False,
    ),
    "category": Prompt(
        text="Challenge category",
        type=None,
        default=None,
        required=True,
        multiple=False,
    ),
    "description": Prompt(
        text="Challenge description shown to the user",
        type=None,
        default=None,
        required=True,
        multiple=False,
    ),
    "value": Prompt(
        text="How many points your challenge should be worth",
        type=int,
        default=None,
        required=True,
        multiple=False,
    ),
    "version": Prompt(
        text="What version of the challenge specification was used",
        type=None,
        default="0.1",
        required=False,
        multiple=False,
    ),
    "image": Prompt(
        text="Docker image used to deploy challenge",
        type=None,
        default=None,
        required=False,
        multiple=False,
    ),
    "type": Prompt(
        text="Type of challenge",
        type=None,
        default="standard",
        required=True,
        multiple=False,
    ),
    "attempts": Prompt(
        text="How many attempts should the player have",
        type=int,
        default=None,
        required=False,
        multiple=False,
    ),
    "flags": Prompt(
        text="Flags that mark the challenge as solved",
        type=None,
        default=None,
        required=False,
        multiple=True,
    ),
    "tags": Prompt(
        text="Tag that denotes a challenge topic",
        type=None,
        default=None,
        required=False,
        multiple=True,
    ),
    "files": Prompt(
        text="Files to be shared with the user",
        type=None,
        default=None,
        required=False,
        multiple=True,
    ),
    "hints": Prompt(
        text="Hints to be shared with the user",
        type=None,
        default=None,
        required=False,
        multiple=True,
    ),
    "requirements": Prompt(
        text="Challenge dependencies that must be solved before this one can be attempted",
        type=None,
        default=None,
        required=False,
        multiple=True,
    ),
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


def lint_challenge(self, challenge):
    required_fields = ["name", "author", "category", "description", "value"]
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
