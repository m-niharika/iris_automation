import sys

from colorama import init
from pandas._libs import json
from os import path, walk
import hashlib
import subprocess
import Constants
from colorama import Fore, Style

# Read conf.json file"
with open(Constants.CONF_FILE, 'rb') as json_file:
    conf_info = json.load(json_file)
    data_Conf_file = conf_info['dataConf_path']
    code_conf_file = conf_info['codeConf_path']
    data_dir_path = conf_info['data_path']
    code_dir_path = conf_info['code_path']
    Key_Id = conf_info['Key']
    Secret_Access_Key = conf_info['Secret_Access_Key']

with open(sys.argv[1], 'rb') as json_file:
    user_inputs = json.load(json_file)

# Generate dvc commands by reading the input from user_inputs.json file for various dvc stages.
def generateCommand(stage,user_inputs):
    dependentVariable = 0
    outputVariable = 0
    command = Constants.DVC_INITIAL_COMMAND
    if (stage == Constants.EVALUATION_STAGE):
        command = Constants.DVC_FINAL_COMMAND
    while dependentVariable < (len((user_inputs[stage])[Constants.DEPENDENCY])):
            command = command+ " -d " +   (((user_inputs[stage])[Constants.DEPENDENCY])[dependentVariable])
            dependentVariable+=1
    while outputVariable < (len((user_inputs[stage])[Constants.OUTPUT])):
            command = command + " -o " + (((user_inputs[stage])[Constants.OUTPUT])[outputVariable])
            outputVariable += 1
    command = command + " "+Constants.EXECUTION_COMMAND+" "+ ((user_inputs[stage])[Constants.CODE])

    return command

# This function generates the checksum of all the files present inside code and data directory
def get_checksum(files,path):
    checksum_lst = []
    for file in files:
        file_path = path +'/'+file

        hasher_object = hashlib.md5()
        with open(file_path,'rb') as open_file:
            content = open_file.read()
            hasher_object.update(content)
        checksum_lst.append(hasher_object.hexdigest())
    zip_object = zip(files , checksum_lst)
    return dict(zip_object)

# This function stores the checksum of files present in data directory into a different file in the form of json
def update_dataConffile(dict):
    with open(data_Conf_file, 'w+') as outfile:
        json.dump(dict, outfile)

# This function stores the checksum of files present in code directory into a different file in the form of json
def update_codeConffile(dict):
    with open(code_conf_file, 'w+') as outfile:
        json.dump(dict, outfile)

# This function gives the directory structure i.e. generates the list of files and subdirectories present inside a directory
def dir_structure(dir_path):
    subdirs = []
    files = []
    for root, dirs,filenames in walk(dir_path):
        for subdir in dirs:
            subdirs.append(path.relpath(path.join(root, subdir), dir_path))
        for f in filenames:
            files.append(path.relpath(path.join(root, f), dir_path))
    return files

# This function includes basic git commands like git add, git commit, git push etc, which run whenever a  pipeine is build.
def gitCommands():

    git_status = 'git status -s'
    subprocess.call(git_status, shell=True)

    git_add = 'git add .'
    subprocess.call(git_add, shell=True)

    git_commit = 'git commit -m "updated" .'
    subprocess.call(git_commit, shell=True)

    if(user_inputs[Constants.TAG]!=""):
        tagName = user_inputs[Constants.TAG]
        git_tag = 'git tag -a ' + tagName + ' -m  changes'
        print(git_tag)
        response = subprocess.call(git_tag, shell=True)
        print("tag response", response)

    git_push = 'git push origin develop'
    subprocess.call(git_push, shell=True)

# Set basic git information like gitignore, git remote.
def gitIgnore():
    git_basic=  [ 'echo *.json >> .gitignore',
                  'echo *.pyc >> .gitignore',
                  'echo *.txt >> .gitignore',
                  'git remote add origin https://github.com/m-niharika/iris_automation.git',
                  'git checkout -b develop'
                 ]

    for cmd in git_basic:
        p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             universal_newlines=True, shell=True)
        output = p.communicate()
        print(output)

#Store the information  of data and code into a different txt file
def dataAndCodeInfo():
    data_files = dir_structure(data_dir_path)
    data_dict =  get_checksum(data_files, data_dir_path)
    update_dataConffile(data_dict)

    code_files = dir_structure(code_dir_path)
    code_dict =  get_checksum(code_files, code_dir_path)
    update_codeConffile(code_dict)

#Check if the code or data or both are updated, if so, changes are pushed to github and dvc remote
def checkForUpdates():
    data_changes = False
    code_changes = False
    updated_data_files = dir_structure(data_dir_path)
    updated_data_dict = get_checksum(updated_data_files, data_dir_path)
    updated_code_files = dir_structure(code_dir_path)
    updated_code_dict = get_checksum(updated_code_files, code_dir_path)

    with open(data_Conf_file, 'rb') as json_file:
        last_data_info = json.load(json_file)

    for key in updated_data_dict:
        if key in last_data_info:
            if (updated_data_dict[key] != last_data_info[key]):
                print("updated----", key, updated_data_dict[key])
                print("last-----", key, last_data_info[key])
                data_changes = True

    with open(code_conf_file, 'rb') as json_file:
        last_code_info = json.load(json_file)

    for key in updated_code_dict:
        if key in last_code_info:
            if (updated_code_dict[key] != last_code_info[key]):
                code_changes = True
                print("updated----", key, updated_code_dict[key])
                print("last-----", key, last_code_info[key])

    if (code_changes and data_changes):
        update_dataConffile(updated_data_dict)
        update_codeConffile(updated_code_dict)
        dvc_dataupdate = [
                          'dvc add data',
                          'dvc push']
        print("\n \033[93m Both Code and Data files are updated,push changes to dvc remote and github\033[0m")
        for cmd in dvc_dataupdate:
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True,shell=True)
            print(Fore.RED +"\n"+ cmd)
            print(Style.RESET_ALL)
            output=p.communicate()
            print(output)
        gitCommands()

    elif (code_changes):
        print("\n\033[93m Only Code is updated, push changes to github \033[0m")
        update_codeConffile(updated_code_dict)
        gitCommands()

    elif (data_changes):
        update_dataConffile(updated_data_dict)

        dvc_dataupdate = ['dvc add data',
                          'dvc push']
        print("\n \033[93mData files are updated so add updated data to dvc cache and push files to remote server \033[0m")
        for cmd in dvc_dataupdate:
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True,
                                 shell=True)
            print(Fore.RED +"\n"+ cmd)
            print(Style.RESET_ALL)
            output = p.communicate()
            print(output)
        gitCommands()

    else:
        print("\033[91m No updates found \033[0m")



