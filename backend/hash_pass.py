from passlib.context import CryptContext
from db_connection import get_connection

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def looks_like_bcrypt(s):
    return s and (s.startswith("$2a$") or s.startswith("$2b$") or s.startswith("$2y$"))

conn = get_connection()
try:
    with conn.cursor() as cur:
        cur.execute("SELECT Email, HashPassword FROM Customer")
        users = cur.fetchall()
        
        updated = 0
        for user in users:
            email = user["Email"]
            pwd = user["HashPassword"]
            
            if looks_like_bcrypt(pwd):
                continue  # đã hash, bỏ qua
            
            hashed = pwd_context.hash(pwd)
            cur.execute("UPDATE Customer SET HashPassword=%s WHERE Email=%s", (hashed, email))
            updated += 1

    conn.commit()
    print(f"Đã hash và cập nhật {updated} password")
finally:
    conn.close()
