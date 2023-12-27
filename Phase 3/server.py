import socket
import threading
import hashlib
import sqlite3
import sys
# import colorama
# from colorama import Back,Fore ,Style

# colorama.init(autoreset=True)

host = '127.0.0.1'
port = 56789

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()

chat_rooms = {}
clients = {}

#------------------------------------------------------------------------------------------------------------
def Client_authentication(Username, Password):
    conn = sqlite3.connect("DataBase.db")
    cur = conn.cursor()

    # Hash the provided password before comparing
    hashed_password = hashlib.sha256(Password.encode()).hexdigest()

    cur.execute("SELECT * FROM Client_Data WHERE USERNAME = ? AND PASSSWORD = ?", (Username, hashed_password))
    if cur.fetchall():
        # check if the client is not already online and the same user name is signing in
        for key in clients:
            if clients[key][0]==Username:
                return False
            else:
                return True
    else:
        return False
#------------------------------------------------------------------------------------------------------------

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
#------------------------------------------------------------------------------------------------------------
def add_new_user(unique_username, hashed_password):
    connection = sqlite3.connect("DataBase.db")
    cur = connection.cursor()
    cur.execute("INSERT INTO Client_Data (USERNAME, PASSSWORD) VALUES (?, ?)", (unique_username, hashed_password))
    connection.commit()
#------------------------------------------------------------------------------------------------------------
def create_chat_room(client):
    # send client a prompt to enter name of new chat room
    client.send("Enter the name of the new chat room:\n ".encode())
    # response from client
    room_name = client.recv(1024).decode()

    # check that chat room doesn't already exist.
    if room_name not in chat_rooms:
        # update list of clients in chat room
        chat_rooms[room_name] = [client]
        client.send(f"Chat room '{room_name}' created!\n".encode())
        client.send(f"Type [/exit] if you want to exit the chat room!\n".encode())

        while True:
            # receive message from a user in chat room
            chat_message = client.recv(1024).decode()

            # if received message is the exist flag, user will exit the chatroom and will be removed from the chat room.
            if chat_message == '/exit':
                client.send(f"You exited chatroom: {room_name}".encode())
                broadcast_chatroom(client,f"exited the chat room!\n", room_name)
                # remove client from the list after he exits the chat room.
                chat_rooms[room_name].remove(client)
                
                if len(chat_rooms[room_name].values) == 0:
                    delete_chatroom(room_name)
                break
            else:
                broadcast_chatroom(client,f"{chat_message}", room_name)
    else:
        client.send(f"Chat room '{room_name}' already exists. Choose a different name.\n".encode())



#------------------------------------------------------------------------------------------------------------
def join_chat_room(client, room_name):
    # if no room name is passed as an argument the user is asked to provide the room name.
    if room_name == '':
        client.send("Enter the name of the chat room you want to join: \n".encode())
        room_name = client.recv(1024).decode()

    # room is check to already exist.
    if room_name in chat_rooms:

        # from here we send the info about the clients
        client.send("successfully joined chat Room") #protocol we can change it later on
        client.send(chat_rooms[room_name])  #send list of clients in chat room  
        # client.send("All in chat Room") 
        # client is appended to the members list
        chat_rooms[room_name].append(client)
        client.send(f"Happy Chatting :)\n".encode())
        client.send(f"Type [/exit] if you want to exit the chat room at any Time!\n".encode())

        broadcast_chatroom(client,f"has joined the chat!\n", room_name) #loon a5dar


        # while True:
        #     chat_message = client.recv(1024).decode()

        #     if chat_message == '/exit':
        #         client.send(f"You exited chatroom: {room_name}".encode())
        #         broadcast_chatroom(client,f"has exited the chat room!\n", room_name) #loon a7mar
        #         chat_rooms[room_name].remove(client)
        #         delete_chatroom(room_name)
        #         break
        #     else:
        #         broadcast_chatroom(client,f"{chat_message}", room_name)
    else:
        client.send(f"Chat room '{room_name}' does not exist. Create the room or choose another.\n".encode())

#------------------------------------------------------------------------------------------------------------
def show_available_chat_rooms(client):

    #checking if the chat Room dictionary is empty or not 
    if len(chat_rooms): 
        client.send("Available Chat Rooms:\n".encode())
        # print list of all chat rooms
        for room in chat_rooms:
            client.send(f"{room}\n".encode())

        # user is prompted to enter a chat room in list. (if desired)
        client.send("Enter the name of the Chat Room you want to join or type [/back] to go back: \n".encode())
        room_choice = client.recv(1024).decode()
        while True:
            # user want to go back to menue
            if room_choice == '/back':
                return
            
            # user entered an existing chatroom name 
            elif room_choice in chat_rooms:
                join_chat_room(client, room_choice)
                # dont forget that I will return from the "join_chat_room" fucntion if the client exited from the function
                return
            
            # entering invalid command
            else:
                client.send(f"Invalid chat room choice. OR invalid Command.\n".encode())
                client.send("Enter the name of the Chat Room you want to join or type [/back] to go back:\n ".encode())
                room_choice = client.recv(1024).decode()

    else :  #in case there is no chat Rooms
        
        client.send("There is No Available chat Rooms :( \n".encode())
        client.send("type [/back] to go back\n".encode())
        respond=client.recv(1024).decode()
        while True:
            if respond=="/back":
                return
            else:
                client.send(f"Invalid Command,Please Enter A valid command\n".encode())
                respond=client.recv(1024).decode()
                


#------------------------------------------------------------------------------------------------------------
# Delete a chatroom
def delete_chatroom(room_name):
    # chatroom is deleted if number of members reaches zero.
    if room_name in chat_rooms and len(chat_rooms[room_name]) == 0:
        del chat_rooms[room_name]
        print(f"Chat room '{room_name}' has been deleted.")
# ------------------------------------------------------------------------------------------------------------

def is_unique(UserName):
    conn = sqlite3.connect("DataBase.db")
    cur = conn.cursor()

    cur.execute("SELECT * FROM Client_Data WHERE USERNAME = ?", (UserName,))
    if cur.fetchall():
        return True
    else:
        return False
#------------------------------------------------------------------------------------------------------------
def is_strong(client, password):
    while len(password) < 5:
        client.send("Weak password! Please choose a password with 5 or more characters\n".encode())
        password = client.recv(1024).decode()
    return password
#------------------------------------------------------------------------------------------------------------
def change_nickname(client, nickname):
    # send a prompt to the client to enter his new nickname
    client.send("Enter new nickname: ".encode())
    # received response from the client
    new_nickname = client.recv(1024).decode()
    # updated the client's nickname
    clients[client][1] = new_nickname
    # printed the new nickname in the server log
    print(f'Nickname of the client {nickname} is now changed to {new_nickname}!\n')
    # notified all clients of the new nickname
    broadcast(f'{nickname} is now called as "{new_nickname}"\n'.encode('ascii'))
    # notified the client that his nickname has been successfully updated
    client.send(f'Nickname successfully changed to {new_nickname}!\n'.encode('ascii'))

#------------------------------------------------------------------------------------------------------------
def close_app():  #!!!!!!!! add if statement to to remove if existed client in list
    # if a user enters "close!" the flag 'exit flag' is sent to client-side.
    client.send("exit flag".encode())
    # Client connection terminates.
    client.close()
    sys.exit(0)
#------------------------------------------------------------------------------------------------------------
def Logout(client):
    # Broadcast the user's logout to other clients
    broadcast(f'{clients[client][1]} is now offline!\n'.encode('ascii'))
    # Update server log
    print(f"User {clients[client][0]} logged out.\n")

    # Remove the client from the clients dictionary
    del clients[client]

    Login_or_register(client)
#------------------------------------------------------------------------------------------------------------

def Show_Menue(client):
    while True:

        # client.send(str(Fore.WHITE+"Welcome To the Local P2P Chatting Application\n").encode())
        client.send("Welcome To the Local P2P Chatting Application\n".encode())
        client.send("1- Press [1] To See Online Users\n".encode())
        client.send("2- Press [2] To create Chat Room\n".encode())
        client.send("3- Press [3] To Join Chat Room\n".encode())
        client.send("4- Press [4] To See Available ChatRooms\n".encode())
        client.send("5- Press [5] To initiate one-to-one chatting Room\n".encode())
        client.send("6- Press [6] To Change your Nickname \n".encode())
        client.send("7- Press [7] To logout\n".encode())
        client.send("8- Press [8] To Close The application\n".encode())

        Respond = client.recv(1024).decode()

        if Respond == '1':
            show_Online(client)
        elif Respond == '2':
            create_chat_room(client)
        elif Respond == '3':
            join_chat_room(client, room_name='')
        elif Respond == '4':
            show_available_chat_rooms(client)
        elif Respond == '5':
            pass
        elif Respond == '6':
            change_nickname(client, clients[client][1])
        elif Respond == '7':
            Logout(client)
        elif Respond == '8':
            close_app()
#------------------------------------------------------------------------------------------------------------

def show_Online(client):
    client.send("Online Users:\n".encode())
    for key in clients:
        client.send(f"(({clients[key][0]})) AKA '{clients[key][1]}'\n".encode())
    client.send("\n1-Enter [R] to return to the Menue \n".encode())
    client.send("\n2-Enter [Close!] to Close the Application \n".encode())

    Respond = client.recv(1024).decode()
    while True:

        if Respond.lower() == 'r':
            return
        elif Respond.lower() == 'Close!':
            pass
        else:
            client.send("Please enter a valid command!\n".encode())
            Respond = client.recv(1024).decode()

        
#------------------------------------------------------------------------------------------------------------

# !!!!!!!!!! handle same login username 
def Login_or_register(client): 
    # client.send(str(Fore.WHITE+"Welecome To the Local P2P Chatting Application\n").encode())
    client.send("Welcome To the Local P2P Chatting Application\n".encode())
    client.send("1- Enter [login] to login\n".encode())
    client.send("2- Enter [Register] if You are New!\n".encode())
    client.send("3- Enter [Close!] if You want to leave the chatting application\n".encode())
    respond = client.recv(1024).decode()

    while True:
        if respond.lower() == "login":
            client.send("Username :".encode())
            Username = client.recv(1024).decode()
            client.send("Password :".encode())
            Password = client.recv(1024).decode()  # Receive the password directly

            status = Client_authentication(Username, Password)

            if status:
                client.send("Login Successful !\n".encode())
                # usernames.append({Username:None})
                return Username
            else:
                client.send("Wrong UserName or Password! OR The user is already online!\n".encode())
                client.send("Choose Your Command again\n".encode())
                respond = client.recv(1024).decode()

        elif respond.lower() == "register":
            client.send("Please enter a Unique Username\n".encode())
            unique_username = client.recv(1024).decode()
            status = is_unique(unique_username)

            if status:
                client.send("This Username Has been Taken.\n".encode())
            else:
                respond = Client_Registration(client, unique_username)

        elif respond.lower() == "close!":
            close_app()

        else:
            client.send("Please enter A valid Command !\n".encode())
            respond = client.recv(1024).decode()
#------------------------------------------------------------------------------------------------------------

def broadcast(message):
    for client in clients:
        client.send(message)
#------------------------------------------------------------------------------------------------------------
# Broadcasts a message to all members of a specific chat room.
def broadcast_chatroom(client,message, room_name):
    if room_name in chat_rooms:
        for c in chat_rooms[room_name]:
            if c==client:
                continue
            else:
                c.send(f"{clients[client][1]}: {message}\n".encode())
#------------------------------------------------------------------------------------------------------------

# def handle(client):
#     while True:
#         try:
#             message = client.recv(1024)
#             broadcast(message)

#         except:

#             print(f"Lost connection with {clients[client][1]}")
#             broadcast(f'{clients[client][1]} is now offline!'.encode())
           
#             client.close()
#             del clients[client]
#             break
#------------------------------------------------------------------------------------------------------------

def Handle_Client(client,address):
    while True:
        try:
            Username = Login_or_register(client)

            print(f"Connected with {str(address)}")

            client.send('Choose Your Nickname'.encode('ascii'))
            nickname = client.recv(1024).decode('ascii')
            clients[client] = [Username, nickname,address]

            print(f'Nickname of the client is {nickname}!')
            broadcast(f'{Username} is now online! as "{nickname}"'.encode('ascii')) #e3meli loon le username , we loon lel nickname 
            client.send('Connected to the server!\n'.encode('ascii'))
            
            Show_Menue(client)
            # thread = threading.Thread(target=handle, args=(client,))
            # thread.start()
        except:
            print(f"Lost connection with  {str(address)}")
            # client may get disconnected before saving or appending his data (login) 
            if client in clients:
                broadcast(f'{clients[client][0]} is now offline!'.encode())
                client.close()
                del clients[client]
                break
            else:
                client.close()
                break

        
#------------------------------------------------------------------------------------------------------------
       
print("Server is listening...")

while True:
    client, address = server.accept()
    threading.Thread(target=Handle_Client,args=(client, address)).start()
