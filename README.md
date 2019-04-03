# Change server passwords

This script is designed to make life easier when changing lots of passwords on servers. It uses the default linux password manager (password-store or pass) to get the passwords from your machine and then auto update them on the server and your machine. 

This script is made in python and needs only one pre-requisite
--Paramiko
You can install paramiko via ``pip install paramiko``

## IMPORTANT
This accepts servers in the form of just names, this can be easily changed by commenting out the line in the change.py file that says CHANGE ME and replacing the server list with url lists.
I.E going from google to google.com


