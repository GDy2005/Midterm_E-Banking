from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel, EmailStr

import random, smtplib

app = FastAPI()

# ====== Database Dependency ======
def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

# ====== Send OTP Request ======
class sendOTPReq(BaseModel):
    email: EmailStr

class VerifyOTPReq(BaseModel):
    email: EmailStr
    otp: str

# ====== Function ======
def generate_otp():
    return 0
    # Code tạo otp

def send_email(email, otp):
    return 0
    # Code gửi mã otp qua email

# ====== API Routes ======
@app.post("/sendotp")
def sendOTP(requestOTP: VerifyOTPReq, db: Session = Depends(get_db)):
    return 0
    # Code xử lý tạo otp và gửi otp tới email

@app.post("/verifyotp")
def verifyOTP(request: VerifyOTPReq, db: Session = Depends(get_db)):
    return 0
    # Code Xác thực OTP người dùng nhập