import psycopg2

#Establishing the connection
conn = psycopg2.connect(
   database="mydb", user='postgres', password='marmak', host='127.0.0.1', port= '5432'
)
#Creating a cursor object using the cursor() method
cursor = conn.cursor()

#Doping EMPLOYEE table if already exists.
cursor.execute("DROP TABLE IF EXISTS users")

#Creating table as per requirement
sql ='''CREATE TABLE users(
   user_id int Primary Key,
   username CHAR(50),
   chat_id int
)'''
cursor.execute(sql)
print("Table created successfully........")
conn.commit()
#Closing the connection
conn.close()