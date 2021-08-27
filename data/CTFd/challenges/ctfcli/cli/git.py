import subprocess

class GitOperations():
    def __init__(self):
        pass

    def get_git_repo_head_branch(self,repo):
        """
        A helper method to get the reference of the HEAD branch of a git remote repo.
        https://stackoverflow.com/a/41925348
        """
        out = subprocess.check_output(["git", "ls-remote", "--symref", repo, "HEAD"]).decode()
        head_branch = out.split()[1]
        return head_branch

    def addchallengerepo(self, repo:str):
        """
        Create a git repository with a ``master`` branch and ``README``.

        :param test_case: The ``TestCase`` calling this.
        """
        try:
            # the user indicates a remote repo, by supplying a url
            if re.match(r'^(?:http|https)?://', repo) or repo.endswith(".git"):
                git.Repo.clone(repo)  
            #user passed a directory
            elif os.isdir(repo):
                repository = git.Repo.init(path=repo)
                repository.index.add()
                repository.index.add(['README'])
                repository.index.commit('Initial commit')
                repository.create_head('master')
        except Exception:
            errorprinter()

        #config = load_config()
        #config["challenges"][self.challengesfolder] = repo

