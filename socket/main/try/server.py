import socket
from threading import Thread

HOST = '127.0.0.1'
PORT = 8000
clients = {}

def handle_client(conn, addr):
    print(f'Connected by {addr}')
    client_connected = True
    client_name = None

    while client_connected:
        try:
            data = conn.recv(1024)
            if not data:
                client_connected = False
                break
            command = data.decode().strip()

            if command.startswith('/name'):
                name = command[6:].strip()
                if name in clients.values():
                    conn.sendall(b'Name already taken')
                else:
                    clients[conn] = name
                    conn.sendall(b'Name accepted')
                    print(f'{name} joined')
                    client_name = name

            elif command.startswith('/kick'):
                target_name = command[6:].strip()
                kicked = False
                for client, client_name in list(clients.items()):  # Iterate over a copy of the dictionary
                    if client_name == target_name:
                        client.sendall(b'You have been kicked')
                        client.close()
                        del clients[client]
                        print(f'{target_name} has been kicked')
                        if client is conn:
                            client_connected = False
                        kicked = True
                        break
                if not kicked:
                    conn.sendall(b'User not found')

            else:
                conn.sendall(b'Invalid command')

        except ConnectionAbortedError:
            client_connected = False

    conn.close()
    if client_name and conn in clients:
        del clients[conn]
        print(f'{client_name} left')

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print(f'Server listening on {HOST}:{PORT}')

    while True:
        conn, addr = s.accept()
        thread = Thread(target=handle_client, args=(conn, addr))
        thread.start()