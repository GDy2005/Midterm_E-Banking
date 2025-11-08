import pymysql

def get_connection():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="",
        database="db_ebank",
        cursorclass=pymysql.cursors.DictCursor
    )