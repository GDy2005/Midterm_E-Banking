from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from datetime import timedelta
from db_connection import get_db

import random, smtplib, redis

app = FastAPI()

# ====== Redis Connection ======
r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# ====== Send OTP Request ======
class sendOTPReq(BaseModel):
    email: EmailStr

class VerifyOTPReq(BaseModel):
    email: EmailStr
    otp: str

# ====== Function ======
def generate_otp():
    return str(random.randint(100000,999999))

def send_email(email, otp):
    return 0
    # Code gửi mã otp qua email

# ====== API Routes ======
@app.post("/sendotp")
def sendOTP(requestOTP: sendOTPReq, db = Depends(get_db)):
    otp_code = generate_otp()
    ttl_seconds = 300  #expire in 5 mins

    r.setex(requestOTP.email, ttl_seconds, otp_code)

    send_email(requestOTP.email, otp_code)

    return {"message": "Vui lòng xác thực mã xác nhận vừa gửi trong email bạn"}

@app.post("/verifyotp")
def verifyOTP(requestOTP: VerifyOTPReq, db = Depends(get_db)):
    otp_stored = r.get(requestOTP.email)

    if not otp_stored:
        raise HTTPException(status_code=404, detail="OTP expired or not found")
    
    if otp_stored != requestOTP.otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")
    
    r.delete(requestOTP.email)

    return {"message": "OTP verified successfully"}