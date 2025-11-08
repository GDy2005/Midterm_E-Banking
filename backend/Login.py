from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from jose import jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from db import get_connection

app = FastAPI()

SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 120

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class LoginRequest(BaseModel):
    email: str
    password: str

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

@app.post("/login")
def login(request: LoginRequest):
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM Customer WHERE Email=%s", (request.email,))
        user = cur.fetchone()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not pwd_context.verify(request.password, user["HashPassword"]):
        raise HTTPException(status_code=401, detail="Invalid password")

    token = create_access_token({"sub": user["Email"]})
    conn.close()

    return {"access_token": token, "token_type": "bearer"}
