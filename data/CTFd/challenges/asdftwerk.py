# Required sections
name: "{{cookiecutter.name}}"
author: "author"
category: category
description: This is a sample description
value: 100
type: standard

# To use the extra fields, set the type to "dynamic"
# extra:
#     initial: 500
#     decay: 100
#     minimum: 50

# Settings used for Dockerfile deployment
# If not used, remove or set to null
# image url (e.g. python/3.8:latest, registry.gitlab.com/python/3.8:latest)
# Follow Docker best practices and assign a tag
image: null

# Optional settings
# connection_info is used to provide a link, hostname, or instructions on how to connect to a challenge
connection_info: nc hostname 12345
# Can be removed if unused
attempts: 5
# Flags specify answers that your challenge use. You should generally provide at least one.
# Can be removed if unused
# Accepts strings or dictionaries of CTFd API data
flags:
    # A static case sensitive flag
    - flag{3xampl3}
    # A static case sensitive flag created with a dictionary
    - {
        type: "static",
        content: "flag{wat}",
    }
    # A static case insensitive flag
    - {
        type: "static",
        content: "flag{wat}",
        data: "case_insensitive",
    }
    # A regex case insensitive flag
    - {
        type: "regex",
        content: "(.*)STUFF(.*)",
        data: "case_insensitive",
    }
# Topics are used to help tell what techniques/information a challenge involves
# They are generally only visible to admins
# Accepts strings
topics:
    - information disclosure
    - buffer overflow
    - memory forensics

# Tags are used to provide additional public tagging to a challenge
# Can be removed if unused
# Accepts strings
tags:
    - web
    - sandbox
    - js

# Provide paths to files from the same directory that this file is in
# Accepts strings
files:
    - dist/source.py

# Hints are used to give players a way to buy or have suggestions. They are not
# required but can be nice.
# Can be removed if unused
# Accepts dictionaries or strings
hints:
    - {
        content: "This hint costs points",
        cost: 10
    }
    - This hint is free

# Requirements are used to make a challenge require another challenge to be
# solved before being available.
# Can be removed if unused
# Accepts challenge names as strings or challenge IDs as integers
requirements:
    - "Warmup"
    - "Are you alive"

# The state of the challenge.
# If the field is omitted, the challenge is visible by default.
# If provided, the field can take one of two values: hidden, visible.
state: hidden

# Specifies what version of the challenge specification was used.
# Subject to change until ctfcli v1.0.0
version: "0.1"