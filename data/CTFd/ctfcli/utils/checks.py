from pathlib import Path
import subprocess
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
