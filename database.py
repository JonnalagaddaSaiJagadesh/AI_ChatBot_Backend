import mysql.connector

def connect_db():
    connection = mysql.connector.connect(
        host='localhost',       # or '127.0.0.1'
        user='root',            # use your MySQL username
        password='2362',# use your MySQL password
        database='chatbot'      # the name of the database you created
    )
    return connection
