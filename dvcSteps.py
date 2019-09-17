import subprocess
import sys
import automationService
from pandas._libs import json
from colorama import Fore, Style, init
import Constants

#Coloroma init
init()

#Store the output of DVC Commands in output.txt
path_to_output_file = Constants.COMMAND_OUTPUT_FILE
commandOutput = open(path_to_output_file, 'w+')

# This function includes the initialization steps like git init, dvc init and adding data to dvc cache
def initialization():
    print("\033[93m\n--------Starting Initialization--------\n \033[0m")
    initializeComamnds = ['git init',
                          'dvc init',
                          'dvc add data',
                          'mkdir output',
                          'mkdir prediction'
                          ]
    print(Fore.RED + "\n 'git init' : Initialize Git Repo")
    print("\n 'dvc init': Initialize Dvc Repo")
    print("\n 'dvc add data': Add data to Dvc Cache which will generate a data.dvc file which can be pushed to git later\n")
    print(Style.RESET_ALL)

    for cmd in initializeComamnds:
         p = subprocess.Popen(cmd,stdout=commandOutput, stderr=subprocess.PIPE, universal_newlines=True,shell=True)
         p.communicate()
    with open(path_to_output_file, "r+") as f:
        print(f.read())
        f.truncate(0)

#This function is to run all the commands on the basis of information provided by user to create a pipeline
def dvcRepro():
    print("\033[93m\n--------Repo initialized, Start building pipeline as per the steps mentioned in user inputs-------- \033[0m")
    dvcCommands = []
    with open(sys.argv[1], 'rb') as json_file:
        user_inputs = json.load(json_file)
        for key in user_inputs:
            if(key != Constants.TAG):
                dvcCommands.append(automationService.generateCommand(key,user_inputs))

        for cmd in dvcCommands:
            print(Fore.RED)
            print("\n " + cmd)
            print(Style.RESET_ALL)
            p = subprocess.Popen(cmd,stdin = subprocess.PIPE,stdout=commandOutput, stderr=subprocess.PIPE, universal_newlines=True,shell=True)
            p.communicate()

        with open(path_to_output_file, "r+") as f:
            print(f.read())
            f.truncate(0)


#This function includes the commands to set the dvc remote and push the data to s3
def pushData():
    print("\033[93m\n--------Pipeline is build, Set the remote DVC server and push data into it-------- \033[0m")

    push_data = ['setx AWS_ACCESS_KEY_ID ' + automationService.Key_Id,
                 'setx AWS_SECRET_ACCESS_KEY ' + automationService.Secret_Access_Key,
                 'dvc remote add -d myremote s3://dvcdataaltran/sourcedata/',
                 'dvc push',
                 'dvc pipeline show --ascii'
                 ]

    print(Fore.RED +"\n'dvc remote add -d myremote s3://dvcdataaltran/sourcedata/': Set dvc remote to S3 to store the data")
    print("\n'dvc push': Push data to the remote server")
    print("\n'dvc pipeline show --ascii': Pictorial representation of the Pipeline")
    print(Style.RESET_ALL)

    for cmd in push_data:
        p = subprocess.Popen(cmd,stdin = subprocess.PIPE,stdout=commandOutput, stderr=subprocess.PIPE, universal_newlines=True,shell=True)
        p.communicate()

    with open(path_to_output_file, "r") as f:
        print(f.read())





