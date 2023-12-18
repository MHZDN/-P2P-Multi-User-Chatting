import socket
import threading
import hashlib
import sqlite3

host = '127.0.0.1'
port = 56789

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()

clients = []
nicknames = []

def Client_authentication(Username, Password):
    conn = sqlite3.connect("DataBase.db")
    cur = conn.cursor()

    # Hash the provided password before comparing
    hashed_password = hashlib.sha256(Password.encode()).hexdigest()

    cur.execute("SELECT * FROM Client_Data WHERE USERNAME = ? AND PASSSWORD = ?", (Username, hashed_password))
    if cur.fetchall():
        return True
    else:
        return False

def Client_Registration(client, unique_username):
    client.send("Please Enter a Strong Password".encode())
    New_Password = client.recv(1024).decode()
    New_Password = is_strong(client, New_Password)

    # Hash the password before storing it in the database
    hashed_password = hashlib.sha256(New_Password.encode()).hexdigest()

    add_new_user(unique_username, hashed_password)
    client.send("Congrats, a new Account has been created".encode())
    client.send("Choose Your Command again".encode())
    respond = client.recv(1024).decode()
    return respond

def add_new_user(unique_username, hashed_password):
    connection = sqlite3.connect("DataBase.db")
    cur = connection.cursor()
    cur.execute("INSERT INTO Client_Data (USERNAME, PASSSWORD) VALUES (?, ?)", (unique_username, hashed_password))
    connection.commit()

def is_unique(UserName):
    conn = sqlite3.connect("DataBase.db")
    cur = conn.cursor()

    cur.execute("SELECT * FROM Client_Data WHERE USERNAME = ?", (UserName,))
    if cur.fetchall():
        return True
    else:
        return False

def is_strong(client, password):
    while len(password) < 5:
        client.send("Weak password! Please choose a password with 5 or more characters".encode())
        password = client.recv(1024).decode()
    return password

def Login_or_register(client):
    client.send("Please Enter [login] to login or [Register] if you are New !\n".encode())
    client.send("Enter [Close!] if You want to leave the chatting application".encode())
    respond = client.recv(1024).decode()

    while True:
        if respond.lower() == "login":
            client.send("Username :".encode())
            Username = client.recv(1024).decode()
            client.send("Password :".encode())
            Password = client.recv(1024).decode()  # Receive the password directly

            status = Client_authentication(Username, Password)

            if status:
                client.send("Login Successful !".encode())
                return
            else:
                client.send("Wrong UserName or Password!".encode())
                client.send("Choose Your Command again".encode())
                respond = client.recv(1024).decode()

        elif respond.lower() == "register":
            client.send("Please enter a Unique Username".encode())
            unique_username = client.recv(1024).decode()
            status = is_unique(unique_username)

            if status:
                client.send("This Username Has been Taken.".encode())
            else:
                respond = Client_Registration(client, unique_username)

        elif respond.lower() == "close!":
            pass

        else:
            client.send("Please enter A valid Command !".encode())
            respond = client.recv(1024).decode()

def broadcast(message):
    for client in clients:
        client.send(message)

def handle(client):
    while True:
        try:
            message = client.recv(1024)
            broadcast(message)

        except:
            index = clients.index(client)
            clients.remove(client)
            client.close()
            nickname = nicknames[index]
            print(f"Lost connection with {nickname}")
            broadcast(f'{nickname} is now offline!'.encode())
            nicknames.remove(nickname)
            break

def receive():
    while True:
        client, address = server.accept()
        Login_or_register(client)

        print(f"Connected with {str(address)}")

        client.send('NICK'.encode('ascii'))
        nickname = client.recv(1024).decode('ascii')
        nicknames.append(nickname)
        clients.append(client)

        print(f'Nickname of the client is {nickname}!')
        broadcast(f'{nickname} is now online!'.encode('ascii'))
        client.send('Connected to the server!'.encode('ascii'))

        thread = threading.Thread(target=handle, args=(client,))
        thread.start()

print("Server is listening...")
receive()
