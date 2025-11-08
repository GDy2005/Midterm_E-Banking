from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from db_connection import get_connection
from jose import jwt

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"

class UserReq(BaseModel):
    token: str

def get_current_email(authorization: str = Header(...)):
    try:
        token = authorization.split(" ")[1] 
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="Token missing email info")
        return email
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

# ====== Lấy User Info từ DB ======
def get_userinfo_nav(email: str):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM Customer WHERE Email=%s", (email,))
        user = cur.fetchone()
        if not user:
            return None
        return user
    finally:
        conn.close()

# ====== Endpoint ======
@app.get("/userinfo")
def get_userinfo_route(current_user_email: str = Depends(get_current_email)):
    user = get_userinfo_nav(current_user_email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "UserName": user["UserName"],
        "FullName": user["FullName"],
        "Email": user["Email"],
        "PhoneNumber": user["PhoneNumber"],
        "Balance": user["Balance"]
    }
