''' This script is for automating the process of building pipeline using Dvc. Whenever a new code and data is received a new
    pipeline is created from scratch, and if there is any updation in code or data files the pipeline will be reproduced.
'''
from os import path
from  automationService import gitIgnore,gitCommands,dataAndCodeInfo,checkForUpdates
import dvcSteps

#Create a DVC pipeline for model generation and deployment
def pipelineCreation():
    file_existence = path.exists('Dvcfile')

    if not file_existence:
        print('\033[1m'+"\n****Got new Code, Start Building Pipeline****\n"+'\033[0m')

        #Dvc Initialization Steps
        dvcSteps.initialization()

        #Dvc Pipeline Building
        dvcSteps.dvcRepro()

        # Dvc Push Data
        dvcSteps.pushData()

        # Set gitIgnore and git Remote
        gitIgnore()

        #Run git Comamnds like status, commit, tag, push
        gitCommands()

        #Store data and code checksum info
        dataAndCodeInfo()

    else:
        print("\033[1m\n****Dvcfile already exist, Checking fir updates****\033[0m\n")
        #Check if there is any change in data or code, and push the changes to github and dvc remote.
        checkForUpdates()



























