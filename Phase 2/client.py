import socket
import threading

# Get user input for choosing a nickname
nickname = input("Choose a nickname: ")

# Create a socket object
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to the server (assuming it's running on '127.0.0.1' at port 56789)
client.connect(('127.0.0.1', 56789))


# Function to handle receiving messages from the server
def receive():
    while True:
        try:
            # Receive messages from the server, decode them from ASCII
            message = client.recv(1024).decode('ascii')

            # If the server sends 'NICK', send the chosen nickname to the server
            if message == 'NICK':
                client.send(nickname.encode('ascii'))
            else:
                # Print the received message
                print(message)
        except:
            # If an error occurs during message reception, print an error message
            print("An error occurred")

            # Close the client socket and exit the loop
            client.close()
            break


# Create a thread for receiving messages and start it
receive_thread = threading.Thread(target=receive)
receive_thread.start()
