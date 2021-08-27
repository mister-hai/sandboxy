# instructions

    This directory is your repository of challenges
        You place challenges here according to this structure

    
    challenges
        category1
            challenge1
                challenge.yml
            challenge2
            challenge3
            challenge4
        category2
            challenge1
            challenge2
        category3
            challenge1
            challenge2
            challenge3

    cd to this directory on the command line and Run the command :
        python3 ./ctfd.py --list-categories
    
    Each Folder is a CATEGORY
        Each subfolder is a challenge in that category
    
    The full list of challenges is populated by the command
        python3 ./ctfd.py --populate-challenges
    
    To add a challenge you must follow the specification outlined in
        extras/challenge-template.yaml