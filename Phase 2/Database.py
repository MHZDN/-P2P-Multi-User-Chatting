import sqlite3
import hashlib


def insert_db(username,password):
    connection= sqlite3.connect("DataBase.db")
    cur=connection.cursor()
    cur.execute("INSERT into Client_Data (USERNAME , PASSSWORD ) values (?,?)",(username,hashlib.sha256(password.encode()).hexdigest()))

def Delete_All():
    connection= sqlite3.connect("DataBase.db")
    cur=connection.cursor()
    cur.execute("DELETE FROM Client_Data")

connection = sqlite3.connect("DataBase.db")
cur = connection.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS Client_Data (
            USERNAME VARCHAR(255) PRIMARY KEY,
            PASSSWORD VARCHAR(255) NOT NULL
)
""")
# Delete_All()
# insert_db("admin",hashlib.sha256("admin".encode()).hexdigest())

# password= hashlib.sha256("admin".encode()).hexdigest()

connection.commit()