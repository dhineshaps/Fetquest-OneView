import psycopg2
import bcrypt

# Using keyword arguments
connection = psycopg2.connect(
    database="dvdrental",
    user="postgres",
    password="dhineshaps",
    host="127.0.0.1",
    port="5432"
)

cursor = connection.cursor()

cursor.execute("SELECT * FROM PORTFOLIO where username='Dhinesh'")
print("The number of parts: ", cursor.rowcount)
row = cursor.fetchone()

while row is not None:
    print(row)
    row = cursor.fetchone()
# cursor.execute("SELECT version();")
# data = cursor.fetchone()
# print("Connection established to:", data)

# Closing the connection
