This tool 

# usage
    to start a repository

    host@server$> ctfd.py ctfcli --ctfdurl <URL> --ctfdtoken <TOKEN> init

        This will install the challenges residing in the 

    To sync the 

# Development criteria

    To generate Documentation:

    We use sphinx with google docstrings currently

    cd $DATAROOT/CTFd
    sphinx-apidoc.exe -f -o .\ctfcli\ .
    make html

## Packages

    https://smarie.github.io/python-yamlable/
    pip install yamlable
    
    gitpython, docker-compose, python-docker, fire, cookiecutter
    pyyaml, Pygments, colorama, dotenv

# Creating a Dcoumentation Github Repo

## Make a remote repository then

    echo "# sandboxy_cods" >> README.md
    git init
    git add README.md
    git commit -m "first commit"
    git branch -M main
    git remote add origin https://github.com/mister-hai/sandboxy_docs.git
    git push -u origin main

