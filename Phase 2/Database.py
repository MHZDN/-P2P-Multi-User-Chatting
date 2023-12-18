import sqlite3
import hashlib

connection= sqlite3.connect("DataBase.db")
cur=connection.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS Client_Data (
            USERNAME VARCHAR(255) PRIMARY KEY,
            PASSSWORD VARCHAR(255) NOT NULL
)
""")
def insert_db(username,password):
    connection= sqlite3.connect("DataBase.db")
    cur=connection.cursor()
    cur.execute("INSERT into Client_Data (USERNAME , PASSSWORD ) values (?,?)",(username,hashlib.sha256(password.encode()).hexdigest()))

def Delete_All():
    connection= sqlite3.connect("DataBase.db")
    cur=connection.cursor()
    cur.execute("DELETE FROM Client_Data")

# insert_db("admin",hashlib.sha256("admin".encode()).hexdigest())
# Delete_All()
# password= hashlib.sha256("admin".encode()).hexdigest()

connection.commit()