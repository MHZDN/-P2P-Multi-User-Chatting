import socket
import threading
import hashlib
import sqlite3
from Database import insert_db

host = '127.0.0.1'  # localhost
port = 56789

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create a TCP socket
server.bind((host, port))  # Bind the server socket to the specified host and port
server.listen()  # Start listening for incoming connections

clients = []  # List to store connected client sockets
nicknames = []  # List to store nicknames of connected clients


# ------------------------------------------------------------------------------------------------------------

def Client_authentication(Username,Password):
    conn=sqlite3.connect("DataBase.db")
    cur=conn.cursor()

    cur.execute("SELECT * FROM Client_Data WHERE USERNAME = ? AND PASSSWORD = ? " , (Username,Password))
    if cur.fetchall():
        return True
    else :
        return False
    
# ------------------------------------------------------------------------------------------------------------
    
def Client_Registration(client,Username):
    client.send("Please Enter a Strong PassWord".encode())
    New_Password = client.recv(1024).decode()
    New_Password=is_strong(client,New_Password)
    insert_db(Username,New_Password)
    client.send("Congrats a new Account has been created".encode())
    client.send("Choose Your Command again".encode())
    respond= client.recv(1024).decode()
    return respond
 
# ------------------------------------------------------------------------------------------------------------
def is_unique(UserName):

    conn=sqlite3.connect("DataBase.db")
    cur=conn.cursor()

    cur.execute("SELECT * FROM Client_Data WHERE USERNAME = ? " , (UserName,))
    if cur.fetchall():
        return True
    else :
        return False
    
# ------------------------------------------------------------------------------------------------------------
    
def is_strong(client,password):
    while(len(password)<5) :
        client.send("Weak password! Please choose a password with 5 or more characters".encode())
        password=client.recv(1024).decode()
    return password
# ------------------------------------------------------------------------------------------------------------

def Login_or_register(client):

    client.send("Please Enter [login] to login or [Register] if you are New !\n".encode())
    client.send("Enter [Close!] if You want to leave the chatting application".encode())
    respond = client.recv(1024).decode()

    while True:

        if respond.lower() == "login":

            client.send("Username :".encode())
            Username = client.recv(1024).decode()
            client.send("Password :".encode())
            Password = client.recv(1024)
            Password=hashlib.sha256(Password).hexdigest()

            status=Client_authentication(Username,Password)

            if status:
                client.send("Login Successful !".encode()) 
                return
            else :
                client.send("Wrong UserName or Password!".encode())
                client.send("Choose Your Command again".encode())
                respond = client.recv(1024).decode()

        elif respond.lower() == "register":

            client.send("Please enter a Unique Username".encode())
            unique_username=client.recv(1024).decode()
            status=is_unique(unique_username)

            if status:
                client.send("This Username Has been Taken.".encode())
            else:
              respond= Client_Registration(client,unique_username)


        elif respond.lower() == "close!":

            pass

        else: 

            client.send("Please enter A valid Command !".encode())
            respond = client.recv(1024).decode()
            
# ------------------------------------------------------------------------------------------------------------

def broadcast(message):
    # Send the provided message to all connected clients
    for client in clients:
        client.send(message)

# ------------------------------------------------------------------------------------------------------------

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
            broadcast(f'{nickname} is now offline!'.encode())  # Notify other clients about client's departure
            nicknames.remove(nickname)
            break

# ------------------------------------------------------------------------------------------------------------

def receive():
    # Accept new client connections
    while True:
        client, address = server.accept()  # Accept a new client connection
        Login_or_register(client)
        


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
# ------------------------------------------------------------------------------------------------------------


print("Server is listening...")
receive()  # Start accepting client connections
