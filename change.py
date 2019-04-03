#!/usr/bin/env python

from subprocess import Popen, PIPE, STDOUT, run
import subprocess
import paramiko
import string
import random
import sys
import time
import select

#Generates a random password of specified length
#Includes letters, numbers and some punctuation
def gen_password(stringLength=15):
        random.seed(None)
        """Generate a random string of letters, digits and special characters """
        #The reason for the large amount of .replace is to minimize string conflicts
        password_characters = string.ascii_letters + string.digits + string.punctuation.replace("|", "").replace("\\", "").replace("$", "").replace("'", "").replace("\"", "")
        return ''.join(random.choice(password_characters) for i in range(stringLength))

def main():
    while True:
        file_name = input("Enter file name with servers in list form: ")
        try: 
            with open(file_name, 'r') as f:
                lines = f.readlines()
                break;
        except FileNotFoundError:
            print('File "{}" not found'.format(f))
    for line in lines:
        #To skip formatting comments in the file
        if line[0] != "#":
            #because info is differentiated via spaces
            server_info = line.split(" ")

            #server will always be the first
            server = server_info[0]

            #If no user skip server
            if len(server_info) == 1:
                print("Error: no user specified for {}, Skipping".format(server))
            else:
                for i in range(1, len(server_info)):
                    #This is going through every line and if multiple users
                    #Connect to all of them
                    user = server_info[i]
                    do_everything(str(server), str(user));
    #This just makes the text red
    print("\x1b[1;31m DON'T FORGET TO PUSH PASS TO GIT\x1b[1;31m")

def do_everything(server, user):
    #sometimes the user can have a \n in it so we need to remove it
    if user[len(user) - 1] == "\n":
        print("Last user\n")
        user = user[:-1]
    
    #Retrieving the password from pass
    passwd_cmd = "pass " + server + "/" + user
    
    #This is needed to process stdout from popen
    passwd_obj = Popen(passwd_cmd, shell = True, stdout=PIPE)
    (output, err) = passwd_obj.communicate()
    
    #this is where the passwords are stored
    #Do not convert old directly to a string because it may have a \ in it
    old_passwd = output.decode("utf-8")

    #Getting rid of \n from string
    old_passwd = old_passwd[:-1] 
    new_passwd = gen_password()
   

    #Use this if you have the servers as addresses and not names
    #server_address = server
    
    #CHANGE THIS so that it becomes server.ending
    server_address = server + ".foo.bar"

    #setting up ssh client object
    ssh = paramiko.SSHClient()

    #this is needed to make sure you connect
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
   
    #Basically piping old password and the new passwords directly into passwd
    change_passwd_cmd = "echo -e '" + old_passwd + "\n" + new_passwd + "\n" + new_passwd + "' | passwd " + user + " && echo 'password updated successfully'"

    #Note the && at the end. If the first command succeeds (I.E the password
    #successfully changed), it will print the statement.
    print("========Changing password for " + server + "========")
    print("Important notes about server")
    print("Old password: {}".format(old_passwd))
    print("New password: {}".format(new_passwd))
    print("server address: {}".format(server))
    print("User: {}".format(user))
    
    #This is to try connecting again and again in case it fails
    connection_tries = 0;
    while connection_tries != 3:
        try: 
            ssh.connect(server_address, username=user, password=old_passwd)
            break;
        except paramiko.ssh_exception.AuthenticationException:
            print("Error, Authentication failed, trying again")
            connection_tries += 1
        except paramiko.ssh_exception.SSHException:
            print("Error connecting to host, trying again")
            connection_tries += 1
        time.sleep(0.5)
    
    #This means that we have tried connecting 3 times to the server and failed
    if connection_tries == 3:
        print("Error: Couldn't connect to host, skipping to next")
        return

    
    #change if server takes a particularly long time to connect to
    seconds_to_wait = 5;

    print("\nWaiting {} seconds in order to ensure connection\n".format(seconds_to_wait))
    time.sleep(seconds_to_wait)
    
    connection_tries = 0
    #This whole thing is grabbing stdout from the server
    while connection_tries != 3:
        try:
            ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(change_passwd_cmd)
            while not ssh_stdout.channel.exit_status_ready():
            # Only print data if there is data to read in the channel
                if ssh_stdout.channel.recv_ready():
                    rl, wl, xl = select.select([ssh_stdout.channel], [], [], 0.0)
                    if len(rl) > 0:
                        # Print data from stdout
                        print("=====Server output string=====")
                        #It returns a byte string so need to convert it
                        print(ssh_stdout.channel.recv(1024).decode("utf-8"), end="")
                        print("==============================")
            break;
        except paramiko.ssh_exception.SSHException:
            print("SSH_exception occured, trying again")
            connection_tries += 1
    
    if connection_tries == 3:
        print("Command could not be run, skipping server/user")
        return
    
    print("Command executed successfuly")
    
    ssh.close()
    print("\nssh closed\n")
    
    print("Adding new password to password store", end="")

    #Using stdin to input the password twice
    input_cmd = new_passwd + "\n" + new_passwd + "\n"
    folder_cmd = server + "/" + user
    p = run(['pass', 'insert', folder_cmd, '-f'], stdout=PIPE, input=input_cmd, encoding='ascii')
    print(p.stdout)

if __name__ == '__main__':
    main();
