import socket
import threading
import sys


# Function to handle receiving messages from the server
def receive():
    while True:
        try:
            # Receive messages from the server, decode them from ASCII
            message = client.recv(1024).decode('ascii')
            print(message)
        except:
            # If an error occurs during message reception, print an error message
            # Close the client socket and exit the loop
            client.close()
            break

#------------------------------------------------------------------------------------------------------------

def write():
    while True:
        message = f"{input('')}"
        if message.lower()=="/close!":
            client.close()
            sys.exit(0)
        client.send(message.encode('ascii'))
#------------------------------------------------------------------------------------------------------------

try:
    # Create a socket object
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to the server (assuming it's running on '127.0.0.1' at port 56789)
    client.connect(('127.0.0.1', 56789))




# Create a thread for receiving messages and start it

    receive_thread = threading.Thread(target=receive)
    receive_thread.start()

    write_thread = threading.Thread(target=write)
    write_thread.start()

except:
    print("an error Occurred\n")
    print("Maybe their is No server up and running or we lost the connection with the server!\n")
