This tool 

# usage
    to start a repository, if you want to add to the existing one,
    Add your folders to the correct challenges and set the correct values in

    /ctfcli/repository_settings.py

    host@server$> python ./ctfd/ ctfcli init

        This will install the challenges residing in the /data/CTFd/challenges folder

    A "masterlist.yaml" will be created representing the repository
    as serialized python objects

    To sync the Repository that was created

        host@server$> ctfd.py ctfcli syncrepository --ctfdurl <URL> --ctfdtoken <TOKEN>

    To add folders to the repository you can use

        host@server$> ctfd.py ctfcli ctfdops addchallengefolder
        host@server$> ctfd.py ctfcli gitops clonerepo https://github.com/user/repo.git
    
    However, be warned! you must have the files structured the same as the 
    repository. In the future, Files not matching specification will be moved 
    and archived to the project root


# Development criteria

### To generate Documentation:

    We use sphinx with google docstrings currently

    cd $DATAROOT/CTFd
    sphinx-apidoc.exe -f -o source ctfcli
    make html

### Challenges

    Challenge folders must contain a challenge.yaml file and "handout" and "solution" folders

### handouts and solutions

    Handouts and solutions should be in a folder named "handout" or "solution" 

    Handouts will be tar'd and gzipped if they are not already
        - if there is a single file, it will be uploaded as is
        - if there is a group of files, they will be put in a tar.gz archive
    
    Solutions must be complete-ish enough to teach how to do the thing
        - If there is a single file, it must be either a solution.md file or .tar.gz


## Creating a Dcoumentation Github Repo

    In ~/sandboxy/data/CTFD
        
        git init
        git add .
        <upload to git>
        lol

# Packages

    gitpython, docker-compose, python-docker, fire, cookiecutter
    pyyaml, Pygments, colorama, dotenv


## Make a remote repository

    echo "# sandboxy_cods" >> README.md
    git init
    git add README.md
    git commit -m "first commit"
    git branch -M main
    git remote add origin https://github.com/mister-hai/sandboxy_docs.git
    git push -u origin main
