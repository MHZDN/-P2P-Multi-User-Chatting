import socket
import threading

host = '127.0.0.1'  # localhost
port = 56789

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create a TCP socket
server.bind((host, port))  # Bind the server socket to the specified host and port
server.listen()  # Start listening for incoming connections

clients = []  # List to store connected client sockets
nicknames = []  # List to store nicknames of connected clients


def broadcast(message):
    # Send the provided message to all connected clients
    for client in clients:
        client.send(message)


def handle(client):
    # Handle messages from a specific client
    while True:
        try:
            message = client.recv(1024)  # Receive a message from the client
            broadcast(message)  # Broadcast the message to all clients

        except:
            # If an error occurs, it usually means the client has disconnected
            index = clients.index(client)
            clients.remove(client)
            client.close()
            nickname = nicknames[index]
            print(f"Lost connection with {nickname}")
            broadcast(f'{nickname} is now offline!'.encode('ascii'))  # Notify other clients about client's departure
            nicknames.remove(nickname)
            break


def receive():
    # Accept new client connections
    while True:
        client, address = server.accept()  # Accept a new client connection
        print(f"Connected with {str(address)}")

        client.send('NICK'.encode('ascii'))  # Send a nickname request to the client
        nickname = client.recv(1024).decode('ascii')  # Receive the nickname from the client
        nicknames.append(nickname)  # Add the nickname to the list
        clients.append(client)  # Add the client socket to the list

        print(f'Nickname of the client is {nickname}!')
        broadcast(f'{nickname} is now online!'.encode('ascii'))  # Notify other clients about client's arrival
        client.send('Connected to the server!'.encode('ascii'))  # Send a connection confirmation to the client

        thread = threading.Thread(target=handle, args=(client,))  # Create a new thread to handle the client's messages
        thread.start()


print("Server is listening...")
receive()  # Start accepting client connections
