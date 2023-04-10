from datetime import date

import psycopg2


# # Establishing the connection
# conn = psycopg2.connect(
#     database="mydb", user='postgres', password='marmak', host='127.0.0.1', port='5432'
# )
# # Creating a cursor object using the cursor() method
# cursor = conn.cursor()
#
# # Doping EMPLOYEE table if already exists.
# cursor.execute("DROP TABLE IF EXISTS users")
#
# # Creating table as per requirement
# sql = '''CREATE TABLE users(
#    user_id int Primary Key,
#    username text,
#    chat_id int
# )'''
# cursor.execute(sql)
# print("Table created successfully........")
# conn.commit()

# Closing the connection
# conn.close()

class PostgresClient:  # класс для универсальной работы с базой данных Postgres. Подключение к базе данных, выполнение команд.
    def __init__(self, database: str, user: str, password: str, host: str, port: str):
        self.database = database
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.conn = None
        self.cursor = None

    def create_connection(self):
        self.conn = psycopg2.connect(
            database=self.database, user=self.user, password=self.password, host=self.host, port=self.port)
        self.cursor = self.conn.cursor()
        return self.conn

    def close_connection(self):
        self.conn.close()

    def execute_command(self, command: str, params: tuple = None):
        if self.conn is not None:
            self.cursor.execute(command, params)
            self.conn.commit()
        else:
            raise Exception('Connection is not established')

    def execute_select_command(self, command: str):
        if self.conn is not None:
            self.cursor.execute(command)
            return self.cursor.fetchall()
        else:
            raise Exception('Connection is not established')

    def table_exists(self, table_name: str):
        self.cursor.execute("SELECT EXISTS(SELECT * FROM information_schema.tables WHERE table_name=%s)", (table_name,))
        return self.cursor.fetchone()[0]

# UserActioner - класс для работы с таблицей users. Создание таблицы, добавление пользователя, получение пользователя, обновление даты последнего обновления.
class UserActioner:
    CREATE_USER = """
        INSERT INTO users (user_id, username, chat_id) VALUES (%s, %s, %s)
        """
    GET_USER = """
        SELECT * FROM users WHERE user_id = %s
        """
    UPDATE_LAST_DATE = """
        UPDATE users SET last_updated_date = %s WHERE user_id = %s
        """

    def __init__(self, db_client: PostgresClient):
        self.db_client = db_client

    def setup(self):
        self.db_client.create_connection()

    def shutdown(self):
        self.db_client.close_connection()

    def create_user(self, user_id: int, username: str, chat_id: int):
        self.create_table_users()
        self.db_client.execute_command(command=self.CREATE_USER, params=(user_id, username, chat_id))

    def get_user(self, user_id: int):
        self.create_table_users()
        user = self.db_client.execute_select_command(self.GET_USER % user_id)
        return user[0] if user else []

    def update_last_date(self, user_id: int, last_date: date):
        self.create_table_users()
        self.db_client.execute_command(command=self.UPDATE_LAST_DATE, params=(last_date, user_id))

    def create_table_users(self):
        if not self.db_client.table_exists('users'):
            create_table_users = '''CREATE TABLE users(
               user_id int Primary Key,
               username text,
               chat_id int,
               last_date_date date
            )'''
            self.db_client.execute_command(command=create_table_users)

# # Establishing the connection
# postgres_client = PostgresClient(database="mydb", user='postgres', password='marmak', host='127.0.0.1', port='5432')
# conn = postgres_client.create_connection()
#
# # insert data into table users
# postgres_client.execute_command(command=CREATE_USER, params=(1, 'viemo777', 1))
# postgres_client.execute_command(command=CREATE_USER, params=(2, 'viemo111', 2))
#
# # select data from table users
# print(postgres_client.execute_select_command(GET_USER % (1)))
# print(postgres_client.execute_select_command(GET_USER % (2)))
#
# # Closing the connection
# postgres_client.conn.close()

# postgres_client = PostgresClient(database="mydb", user='postgres', password='marmak', host='127.0.0.1', port='5432')
# user_actioner = UserActioner(db_client=postgres_client)
# user_actioner.setup()
# new_user = {'user_id': 5, 'username': 'viemo555', 'chat_id': 5}
# user_actioner.create_user(**new_user)
#
# user = user_actioner.get_user(user_id=1)
# print(user)
