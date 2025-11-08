import pymysql

def get_connection():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="",
        database="db_ebank",
        cursorclass=pymysql.cursors.DictCursor
    )

def get_db():
    conn = get_connection()
    try:
        yield conn
    finally:
        conn.close()
