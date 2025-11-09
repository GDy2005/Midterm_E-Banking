from fastapi import FastAPI, HTTPException, Header, Depends, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from backend.db_connection import get_connection, get_db
from jose import jwt, JWTError
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
import random, smtplib, redis
from fastapi.middleware.cors import CORSMiddleware

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
def get_tuitioninfo(student_id: int, semester: str = None):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM tuition WHERE Student.StudentID=Tuition.StudentID AND Tuition.Tuition.TuitionID=Transaction AND StudentID=%s AND Semester=%s", (student_id, semester))
        tuitions = cur.fetchall()
        return tuitions
    finally:
        conn.close()

@app.get("/tuitioninfo")
def get_tuitioninfo_route(student_id: str, current_user: dict = Depends(get_current_active_user)):
    user = current_user
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    student_id = user["StudentID"] 
    tuition_list = get_tuitioninfo(student_id)

    if not tuition_list:
        raise HTTPException(status_code=404, detail="No tuition records found")

    return {
        "StudentID": student_id,
        "FullName": user["FullName"],
        "Email": user["Email"],
        "TuitionRecords": [
            {
                "tuitionID": t["tuitionID"],
                "Semester": t["Semester"],
                "Fee": t["Fee"],
                "BeginDate": t["BeginDate"],
                "EndDate": t["EndDate"],
            }
            for t in tuition_list
        ]
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

def generate_otp():
    return str(random.randint(100000,999999))

def send_email(email, otp):
    return 0
    # Code gửi mã otp qua email

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
