This tool 

#### Necessary Packages

    gitpython, docker-compose, python-docker, fire, cookiecutter
    pyyaml, Pygments, colorama, dotenv

#### usage

        FIRST RUN, If you have not modified the repository this is not necessary!
        This will generate a Masterlist.yaml file that contains the contents of the 
        repository for loading into the program
        
        >>> host@server$> python ./ctfcli/ ctfcli init

        you should provide token and url when running the tool, it will store 
        token only for a limited time. This is intentional and will not be changed
        This tool is capable of getting its own tokens given an administrative username
        and password

#### Authentication

        for SINGLE operations, with NO authentication persistance:
        
        >>> host@server$> python ./ctfcli/ ctfcli --ctfdurl <URL> --ctfdtoken <TOKEN>

        for multiple operations, WITH authentication persistance:
        This configuraiton will be able to obtain tokens via CLI
        
        >>> host@server$> python ./ctfcli/ ctfcli --adminusername moop --adminpassword password

#### To sync repository contents to CTFd Server:
        
        >>> host@server$> python ./ctfcli/ ctfcli syncrepository --ctfdurl <URL> --ctfdtoken <TOKEN>

        Replacing <URL> with your CTFd website url
        and replacing <TOKEN> with your CTFd website token
        You can obtain a auth token from the "settings" page in the "admin panel"
        This will initialize the repository, from there, you can either:
        
        Pull a remote repository
        you have to create a new masterlist after this
        That will be covered further down.
        >>> host@server$> ctfd.py gitops createremoterepo https://REMOTE_REPO_URL.git

        Generating a completion script and adding it to ~/.bashrc
        >>> host@server$>python ./ctfcli/ ctfcli -- --completion > ~/.ctfcli-completion
        >>> host@server$> echo "source ~/.ctfcli-completion" >> ~/.bashrc  

        To generate a completion script for the Fish shell. 
        (fish is nice but incompatible with bash scripts so far as I know so start.sh wont work)
        >>> -- --completion fish 

        If the commands available in the Fire CLI change, you'll have to regenerate the 
        completion script and source it again.

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

## Make a remote repository

    echo "# sandboxy_cods" >> README.md
    git init
    git add README.md
    git commit -m "first commit"
    git branch -M main
    git remote add origin https://github.com/mister-hai/sandboxy_docs.git
    git push -u origin main
