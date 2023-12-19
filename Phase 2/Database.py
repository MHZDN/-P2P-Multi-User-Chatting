import sqlite3
import hashlib

connection = sqlite3.connect("DataBase.db")
cur = connection.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS Client_Data (
            USERNAME VARCHAR(255) PRIMARY KEY,
            PASSSWORD VARCHAR(255) NOT NULL
)
""")
def insert(username,password):
    cur.execute("INSERT into Client_Data (USERNAME , PASSSWORD ) values (?,?)",(username,password))

def Delete_All():
    cur.execute("DELETE FROM Client_Data")

Delete_All()
insert("admin",hashlib.sha256("admin".encode()).hexdigest())

# password= hashlib.sha256("admin".encode()).hexdigest()

connection.commit()