import socket
import os
import sys
from time import sleep
import hashlib
import shutil


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

HOST = socket.gethostbyname("") #or IPv4/v6 Address
PORT = 42960
opt_level = "O2"
BUFFER_SIZE = 4096

filename = sys.argv[1]
try:
    opt_level = sys.argv[2]
except Exception:
    pass

try:
    sys.argv[3]
    send_generic_binary = True
except Exception:
    send_generic_binary = False
    pass

def hash_sha512(input_data):
    hash = hashlib.sha512(str(input_data).encode("utf-8")).hexdigest()
    return hash

file_size = os.path.getsize(filename)
encrypted_filename = "{}.aes".format(filename)
encrypted_file = shutil.copy(filename,encrypted_filename)

key = "" #Secret for protecting WebServer

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    s.connect((HOST,PORT))
except Exception as e:
    print(f"{bcolors.FAIL}[!] Connection to GCC-Server failed: {e}")

s.send("{}#CIS#{}#CIS#{}#CIS#{}#CIS#{}".format(encrypted_file, file_size, opt_level,hash_sha512(key),send_generic_binary).encode())
sleep(0.3)
with open(encrypted_filename, "rb") as cpp_file:
    while True:
        bytes_read = cpp_file.read(BUFFER_SIZE)
        if not bytes_read:
            break
        s.sendall(bytes_read)
cpp_file.close()
if opt_level == "O0":
    opt_print = ("□ □ □ □ □ □ □")
if opt_level == "O1":
    opt_print = ("■ □ □ □ □ □")
if opt_level == "O2":
    opt_print = ("■ ■ □ □ □ □")
if opt_level == "O3":
    opt_print = ("■ ■ ■ □ □ □")
if opt_level == "Ofast":
    opt_print = ("■ ■ ■ ■ □ □")
if opt_level == "Og":
    opt_print = ("■ ■ ■ ■ ■ □")
if opt_level == "Os":
    opt_print = ("■ ■ ■ ■ ■ ■")


print(f"{bcolors.OKBLUE}[*] Sent Stage-File with SHA512-PassKey Verification. Waiting for GCC-Compiler Return.\n[*] Optimization-Level: {opt_level} {opt_print}")
if send_generic_binary == True:
    print("Recieve binary...")
    filename,filesize_binary = s.recv(BUFFER_SIZE).decode("UTF-8").split("#SEP#")
    #recv_loops = int(filesize_binary) // BUFFER_SIZE

    with open(filename, "wb") as binary_file:
        while True:
            bytes_read = s.recv(BUFFER_SIZE)
            if not bytes_read:
                break
            binary_file.write(bytes_read)
    print(f"{bcolors.OKGREEN}[*] Recieved binary.")
    s.close()
else:
    message = s.recv(1024)
    while message:
        message = message.decode("UTF-8")
        print(f"{bcolors.OKGREEN}{bcolors.BOLD}{message}")
        message = s.recv(1024)
    s.close()
