This tool 

# usage
    to start a repository

    host@server$> ctfd.py ctfcli init

        This will install the challenges residing in the /data/CTFd/challenges folder

    A "masterlist.yaml" will be created representing the repository
    as serialized python objects

    To sync the Repository that was created

        host@server$> ctfd.py ctfcli syncrepository --ctfdurl <URL> --ctfdtoken <TOKEN>

    To add folders to the repository you can use

        host@server$> ctfd.py ctfcli gitops clonerepo https://github.com/user/repo.git
    
    However, be warned! you must have the files structured the same as the 
    repository. In the future, Files not matching specification will be moved 
    and archived to the project root


# Development criteria

    To generate Documentation:

    We use sphinx with google docstrings currently

    cd $DATAROOT/CTFd
    sphinx-apidoc.exe -f -o source ctfcli
    make html

# Creating a Dcoumentation Github Repo

    In ~/sandboxy/data/CTFD
        
        git init
        git add .
        <upload to git>
        lol

## Packages

    gitpython, docker-compose, python-docker, fire, cookiecutter
    pyyaml, Pygments, colorama, dotenv


## Make a remote repository then

    echo "# sandboxy_cods" >> README.md
    git init
    git add README.md
    git commit -m "first commit"
    git branch -M main
    git remote add origin https://github.com/mister-hai/sandboxy_docs.git
    git push -u origin main

