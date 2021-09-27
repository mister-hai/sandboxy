#!/bin/bash
#ctfd APIv1 Bash Script

## Initial setup.  Make admin user and write cookie for follow-on API calls
nonce=$(curl -s http://127.0.0.1:8000/setup -c cookie | grep 'name="nonce"' | awk '{ print $4 }' | cut -d'"' -f2)
curl "http://127.0.0.1:8000/setup" \
-H "Content-Type: application/x-www-form-urlencoded" \
-b cookie \
--data "nonce=$nonce&ctf_name=test&name=admin&email=test"%"40test&password=foobar&user_mode=users"

## Get current user
curl -X GET "http://127.0.0.1:8000/api/v1/users/me" -H  "accept: application/json" -b cookie

## Make a new user
curl -X POST "http://127.0.0.1:8000/api/v1/users" -H "content-type: application/json" -b cookie -d \
'{"name":"foobar",
"email":"foo@bar.com",
"password":"123",
"type":"user",
"verified":"false",
"hidden":"false",
"banned":"false"}'

## make a new challenge
curl -X POST "http://127.0.0.1:8000/api/v1/challenges" -H "content-type: application/json" -b cookie -d \
'{"name":"somechal",
"category":"hacks",
"state":"hidden",
"value":"9001",
"type":"standard",
"description":"sample challenge"}'

## add a flag to a challnge
curl -X POST "http://127.0.0.1:8000/api/v1/flags" -H "content-type: application/json" -b cookie -d \
'{"challenge":"1",
"content":"eleventy",
"type":"static"}'

## Upload a file to a challenge.  You need to use a nonce from the admin page of the challenge you're editing.
nonce=$(curl -s http://127.0.0.1:8000/admin/challenges/1 -b cookie | grep nonce | cut -d'"' -f2)
curl -X POST "http://127.0.0.1:8000/api/v1/files" -b cookie  \
-F "file=@some-local-file.png" \
-F "nonce=$nonce" \
-F "challenge=1" \
-F "type=challenge"
