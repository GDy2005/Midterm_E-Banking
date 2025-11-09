from fastapi import FastAPI, HTTPException, Header, Depends, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from backend.db_connection import get_connection, get_db
from backend.redis_connection import get_redis_connection
from jose import jwt, JWTError
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
import random, smtplib, redis
from fastapi.middleware.cors import CORSMiddleware
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import secrets
import string
from typing import List, Iterable, Set

app = FastAPI()

# Allow frontend dev server (Live Server) to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 120
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ========= Login API =========
# Request Model
class LoginRequest(BaseModel):
    email: str
    password: str

# Create JWT Token
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    # use numeric UTC timestamp for exp
    to_encode.update({"exp": int(expire.timestamp())})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Verify user
def authenticate_user(email: str, password: str):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM Customer WHERE Email=%s", (email,))
        user = cur.fetchone()
        if not user:
            return None
        if not pwd_context.verify(password, user["HashPassword"]):
            return None
        return user
    finally:
        conn.close()


# Login/token endpoint (OAuth2 password flow)
@app.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["Email"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# POST /login - accept JSON {email, password} (used by frontend) or form-data (OAuth2)
@app.post("/login")
async def login_alias(loginReq: Request):
    input = await loginReq.json()
    email = input.get("email")
    password = input.get("password")

    if not email or not password:
        raise HTTPException(status_code=400, detail="Missing credentials")

    user = authenticate_user(email, password)
    
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    access_token = create_access_token(
        data={"sub": user["Email"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# --- Lấy email hiện tại từ token ---
def get_current_email(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="Token missing email info")
        return email
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

# ========= User API =========
class UserReq(BaseModel):
    token: str



def get_user_by_email(email: str):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM Customer WHERE Email=%s", (email,))
        return cur.fetchone()
    finally:
        conn.close()


async def get_current_active_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = get_user_by_email(email)
    if user is None:
        raise credentials_exception
    return user


@app.get("/userinfo")
def get_userinfo_route(current_user: dict = Depends(get_current_active_user)):
    user = current_user
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "UserName": user["UserName"],
        "FullName": user["FullName"],
        "Email": user["Email"],
        "PhoneNumber": user["PhoneNumber"],
        "Balance": user["Balance"]
    }

# ====== TUITION API ======
def get_tuitioninfo(student_id: str, semester: str = None):
    conn = get_connection()
    try:
        cur = conn.cursor()
        if semester is None:
            cur.execute("SELECT Tuition.*, `Transaction`.`Status` FROM Tuition INNER JOIN `Transaction` ON `Transaction`.TuitionID=Tuition.TuitionID WHERE StudentID=%s AND (`Transaction`.`Status`=\"UNPAID\" OR `Transaction`.`Status`=\"CANCELLED\")", (student_id))
        else:
            cur.execute("SELECT Tuition.*, `Transaction`.`Status` FROM Tuition INNER JOIN `Transaction` ON `Transaction`.TuitionID=Tuition.TuitionID WHERE StudentID=%s AND Semester=%s AND (`Transaction`.`Status`=\"UNPAID\" OR `Transaction`.`Status`=\"CANCELLED\")", (student_id, semester))
        tuitions = cur.fetchall()
        return tuitions
    finally:
        conn.close()

@app.get("/tuitioninfo")
def get_tuitioninfo_route(student_id: str, semester: str = None, current_user: dict = Depends(get_current_active_user)):

    user = current_user
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if semester is None:
        tuition_list = get_tuitioninfo(student_id, semester)
        if not tuition_list:
            raise HTTPException(status_code=404, detail="No tuition records found")
        return {
            student_id: [
                {
                    "TuitionID": t["TuitionID"],
                    "Semester": t["Semester"],
                    "Fee": t["Fee"],
                    "BeginDate": t["BeginDate"],
                    "EndDate": t["EndDate"],
                    "Status": t["Status"]
                } for t in tuition_list
            ]
        }
    else:
        tuition = get_tuitioninfo(student_id, semester)
        if not tuition:
            raise HTTPException(status_code=404, detail="No tuition record found for this semester")
        
        # Lấy Tuition Info ra khỏi List of Tution
        tuition = tuition[0]
        
        return {
            "TuitionID": tuition["TuitionID"],
            "StudentID": tuition["StudentID"],
            "Semester": tuition["Semester"],
            "BeginDate": tuition["BeginDate"],
            "EndDate": tuition["EndDate"],
            "Fee": tuition["Fee"]
        }

# ====== Lấy Student Info từ DB ======
def get_studentinfo(student_id: str):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM Student WHERE StudentID=%s", (student_id,))
        student = cur.fetchone()
        return student
    finally:
        conn.close()

# ====== Student API ======
@app.get("/studentinfo")
def get_studentinfo_route(student_id: str):
    student = get_studentinfo(student_id)
    if not student:  
        raise HTTPException(status_code=404, detail="Student not found")
    return {
        "StudentID": student["StudentID"],
        "FullName": student["FullName"],
        "Email": student["Email"]
    }


r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# ====== OTP API ======
class sendOTPReq(BaseModel):
    email: EmailStr

class VerifyOTPReq(BaseModel):
    email: EmailStr
    otp: str

BLACKLIST: Set[str] = {
    "000000","111111","222222","333333","444444","555555","666666","777777","888888","999999",
    "123456","654321","112233","121212","123123","000123","999000","101010","010101"
}

# --- hàm kiểm tra mẫu ---
def is_sequential(s: str) -> bool:
    """True nếu toàn chuỗi là dãy tăng hoặc giảm liên tiếp (ví dụ '1234' hoặc '4321')."""
    if len(s) < 2:
        return False
    inc = all((int(s[i+1]) - int(s[i]) == 1) for i in range(len(s)-1))
    dec = all((int(s[i]) - int(s[i+1]) == 1) for i in range(len(s)-1))
    return inc or dec

def max_repeat_length(s: str) -> int:
    """Độ dài lớn nhất của chữ số lặp liên tiếp (ví dụ '1112' -> 3)."""
    maxr = 1
    cur = 1
    for i in range(1, len(s)):
        if s[i] == s[i-1]:
            cur += 1
            if cur > maxr:
                maxr = cur
        else:
            cur = 1
    return maxr

def max_run_length(s: str) -> int:
    """Tìm độ dài lớn nhất của một đoạn con liên tiếp (tăng hoặc giảm)."""
    n = len(s)
    if n <= 1:
        return n
    maxrun = 1
    for i in range(n):
        # kiểm tra chạy từ i sang phải
        for j in range(i+1, n):
            sub = s[i:j+1]
            if is_sequential(sub):
                if len(sub) > maxrun:
                    maxrun = len(sub)
    return maxrun

def is_palindrome(s: str) -> bool:
    return s == s[::-1]

def is_half_repeat(s: str) -> bool:
    """Ví dụ 121212 hoặc 123123 (n/2 pattern repeated)."""
    n = len(s)
    if n % 2 != 0:
        return False
    half = s[:n//2]
    return half * 2 == s

# --- quy tắc quyết định 'xấu' hay không ---
def is_ugly_otp(
    s: str,
    blacklist: Iterable[str] = BLACKLIST,
    min_unique_digits: int = 3,
    max_allowed_repeat: int = 3,
    max_allowed_run: int = 3
) -> bool:
    s = str(s)
    if not s.isdigit():
        return False
    if s in set(blacklist):
        return False
    if len(set(s)) < min_unique_digits:
        return False
    if max_repeat_length(s) > max_allowed_repeat:
        return False
    if max_run_length(s) > max_allowed_run:
        return False
    if is_palindrome(s):
        return False
    if is_half_repeat(s):
        return False
    return True

def inRedis(otp_code: str) -> bool:
    r = get_redis_connection()
    for key in r.scan_iter(match="*"):
        value = r.get(key)
        if value == otp_code:
            return True
    return False

def generate_otp():
    # Tạo mã OTP
    otp_code = str(random.randint(100000,999999))
    # Check redis
    while (not is_ugly_otp(otp_code)) or (inRedis(otp_code)): # Check số đẹp
        otp_code = str(random.randint(100000,999999))
    return otp_code

def send_email(email, otp):
    # --- Cấu hình ---
    sender_email = "ngochithuan.dev@gmail.com"
    app_password = "vtvo qxyq aizl aokx"
    receiver_email = email

    # --- Tạo nội dung mail ---
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["Subject"] = "Xác thực giao dịch - OTP của bạn"

    body = """
    Xin chào,

    Mã OTP xác thực giao dịch của bạn là: """+ otp +"""
    OTP này sẽ hết hạn sau 2 phút.

    Trân trọng,
    Hệ thống E-Bank
    """

    msg.attach(MIMEText(body, "plain"))

    # --- Gửi email ---
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()  # mã hóa kết nối
            server.login(sender_email, app_password)
            server.send_message(msg)
            print("Email sent successfully!")
    except Exception as e:
        print("Error:", e)

@app.post("/sendotp")
def sendOTP(requestOTP: sendOTPReq, db = Depends(get_db)):
    otp_code = generate_otp()
    ttl_seconds = 160  #expire in 5 mins

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








