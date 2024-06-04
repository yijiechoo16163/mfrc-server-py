import socket
import threading

HOST = '192.168.100.78'
PORT = 5000
TIMEOUT = 0.1  # Timeout in seconds

def read_user_input(sock):
    while True:
        command = input('Enter command: ')
        if command == 'exit':
            sock.sendall(command.encode())
            break
        sock.sendall(command.encode())

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    name = input('Enter your name: ')
    s.sendall(f'/name {name}'.encode())
    response = s.recv(1024).decode()
    if response == 'Name accepted':
        print('Name accepted')
        input_thread = threading.Thread(target=read_user_input, args=(s,))
        input_thread.daemon = True
        input_thread.start()

        while True:
            try:
                data = s.recv(1024)
                if not data:
                    print('Connection closed by server')
                    break
                server_response = data.decode()
                if server_response == 'You have been kicked':
                    print('You have been kicked')
                    break
                else:
                    print(f'Received: {server_response}')
            except (ConnectionResetError, ConnectionAbortedError):
                print('You have been kicked')
                break
    else:
        print(response)