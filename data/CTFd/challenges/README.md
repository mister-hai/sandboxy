# instructions

    TODO:
        modify/rename all challenge.yml and metadata.yml files to 
            "challenge.yml" 
        and to fit spec

        move/rename all files/folders in challenge folders to 
        fit the following schema

    This directory is your repository of challenges
        You place challenges here according to this structure

    
    /challenges
        # git data
        /.git
        # repository data
        /.ctfcli
        # master list of all challenges
        challengelist.yaml
        /categoryname
            /challenge
                /handout
                    file1.txt
                    file2.tar.gz
                    ...
                /solution
                    file1.txt
                    file2.tar.gz
                    ...
                challenge.yml
                challenge.yaml (kubernetes deployment)
                README.MD

    cd to this directory on the command line and Run the command :
        python3 ./ctfd.py --help
    
    Each Folder is a CATEGORY
        Each subfolder is a challenge in that category
    
    The full list of challenges is populated by the command
        python3 ./ctfd.py --populate-challenges
    
    To add a challenge you must follow the specification outlined in
        extras/challenge-template.yaml