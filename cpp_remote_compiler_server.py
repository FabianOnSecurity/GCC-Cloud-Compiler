import shutil
import socket
import os
import hashlib
import subprocess
import time
from datetime import datetime

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

key = ""
def hash_sha512(input_data):
    hash = hashlib.sha512( str(input_data).encode("utf-8") ).hexdigest()
    return hash

def write_log_file(log_data):
    with open("log_data.log", "a") as log_file:
        log_file.write(log_data)

SERV_HOST = "0.0.0.0"
SERV_PORT = 42960
BUFFER_SIZE = 4096
SEP = "#CIS#"

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((SERV_HOST, SERV_PORT))
s.listen(2)
print(f"{bcolors.OKCYAN}[*] Listening as {SERV_HOST}:{str(SERV_PORT)}")
while True:
    try:
        client_socket, address = s.accept()
        print(f"{bcolors.OKCYAN}[*] Recieve Data from {address[0]}")
        write_log_file(f"{bcolors.OKCYAN}[*] Recieve Data from {address[0]}")
        received = client_socket.recv(BUFFER_SIZE).decode("UTF-8")
        filename, filesize, opt_level,hashed_key, send_binary = received.split(SEP)
        recv_loopes = int(filesize) // BUFFER_SIZE
        if hashed_key == hash_sha512(key):
            filename = os.path.basename(filename)
            decrypted_filename = filename[:len(filename)-4]
            print(f"[*] OPT-Level: {opt_level}")
            filesize = int(filesize)
            start = time.time()
            try:
                with open(filename, "wb") as encrypted_file:
                    for i in range(recv_loopes+1):
                        bytes_read = client_socket.recv(BUFFER_SIZE)
                        encrypted_file.write(bytes_read)
        
                encrypted_file.close()

            except Exception as e:
                print(f"{bcolors.FAIL}[!] Connection-ERROR: {e}")
                write_log_file(f"{bcolors.FAIL}[!] Connection-ERROR: {e}")
            shutil.copy(filename,decrypted_filename)
            print(f"{bcolors.OKGREEN}[+] Successfully retrieved {filename} and decrypted.")

            with open(decrypted_filename, "r") as cpp_file:
                file_exec_code = cpp_file.read()
                if file_exec_code.find("system") != -1:
                    warn_message = f"{bcolors.WARNING}[!] Exploit-Prevention: Compiling stopped.\n"
                    print(warn_message)
                    client_socket.send(bytes(f"{bcolors.WARNING}[!] System-Commands are not allowed to execute!","utf-8"))
                    write_log_file(warn_message)

                else:   

                    binary_name = decrypted_filename[:len(decrypted_filename)-4]
                    now = datetime.now()
                    def send_command(command):
                        try:
                            output = str(subprocess.check_output(command, shell=True).decode("UTF-8"))
                            message = output.replace('0','')
                            if message != "":
                                message = f'''\n--------Execution Code | {now.strftime("%d/%m/%Y %H:%M:%S")}-------\n\n{message}\n\n----------Code-End | {now.strftime("%d/%m/%Y %H:%M:%S")}----------\n'''
                                print(message)
                                write_log_file(message)
                                client_socket.send(bytes(str(message),"utf-8"))
                            return True
                        except Exception as e:
                            command = "{} 2> fallback.log".format(command)
                            output = os.system(command)
                            with open("fallback.log", "r") as fallback:
                                output = fallback.read()
                            fallback.close()
                            os.remove("fallback.log")
                            message = f"{bcolors.FAIL}\n--------Error in Code-------\n\n{output}\n\n----------Error-End---------\n"
                            print(message)
                            write_log_file(message)
                            client_socket.send(bytes(str(message),"utf-8"))
                            client_socket.close()
                            return False

                    try:
                        start_time_1 = time.time()
                        if send_binary == "False":
                            correct = send_command(f"gcc {decrypted_filename} -lstdc++ -o {binary_name} -{opt_level}")
                        elif send_binary == "True":
                            correct = send_command(f"gcc {decrypted_filename} -lstdc++ -o {binary_name} -{opt_level} -mtune=generic -march=x86-64")
                        if correct == True:
                            if send_binary == "True":
                                print("[*] Sending Generic Binary to Client...")
                                binary_filesize = os.path.getsize(binary_name)
                                
                                with open(binary_name, "rb") as binary:
                                    client_socket.send("{}#SEP#{}".format(binary_name,binary_filesize).encode())
                                    time.sleep(0.3)
                                    while True:
                                        bytes_read = binary.read(BUFFER_SIZE)
                                        if not bytes_read:
                                            break
                                        client_socket.sendall(bytes_read)
                                    client_socket.close()
                            else:
                                send_command(f"chmod +x {binary_name}")
                                end_time_1 = time.time()
                                start_time_2 = time.time()
                                send_command(f"./{binary_name}")
                                end_time_2 = time.time()

                                print(f"{bcolors.OKCYAN}[*] Compilation-Time: {round(end_time_1-start_time_1,6)}s\n[*] Execution-Time: {round(end_time_2-start_time_2,6)}s")
                                client_socket.send((bytes(f"[*] Compilation-Time: {round(end_time_1-start_time_1,6)}s\n[*] Execution-Time: {round(end_time_2-start_time_2,6)}s", "utf-8")))
                            
                    except ConnectionAbortedError as e:
                        print(f"{bcolors.WARNING}[!] Error: {e}")

        else:
            print(f"{bcolors.WARNING}[!] Unauthorized Login-Try!")
            write_log_file(f"{bcolors.WARNING}[!] Unauthorized Login-Try!\n")
        
        client_socket.close()
        try:
            os.remove(decrypted_filename)
            os.remove(binary_name)
            os.remove(filename)
        except Exception:
            pass

    except Exception as e:
        print(f"{bcolors.WARNING}[!] Error: {e}") 
