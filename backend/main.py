from fastapi import FastAPI, HTTPException, Header, Depends, status, Request, Body
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
import pymysql.cursors
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
<<<<<<< Updated upstream
        cur.execute("SELECT * FROM tuition WHERE Student.StudentID=Tuition.StudentID AND Tuition.Tuition.TuitionID=Transaction AND StudentID=%s AND Semester=%s", (student_id, semester))
=======
        if semester is None:
            cur.execute("SELECT Tuition.*, `Transaction`.`Status` FROM Tuition INNER JOIN `Transaction` ON `Transaction`.TuitionID=Tuition.TuitionID WHERE StudentID=%s AND (`Transaction`.`Status`=\"UNPAID\" OR `Transaction`.`Status`=\"CANCELLED\")", (student_id))
        else:
            cur.execute("SELECT Tuition.*, `Transaction`.`Status` FROM Tuition INNER JOIN `Transaction` ON `Transaction`.TuitionID=Tuition.TuitionID WHERE StudentID=%s AND Semester=%s AND (`Transaction`.`Status`=\"UNPAID\" OR `Transaction`.`Status`=\"CANCELLED\")", (student_id, semester))
>>>>>>> Stashed changes
        tuitions = cur.fetchall()
        return tuitions
    finally:
        conn.close()

@app.get("/tuitioninfo")
def get_tuitioninfo_route(student_id: str, current_user: dict = Depends(get_current_active_user)):
    user = current_user
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if semester is None:
        tuition_list = get_tuitioninfo(student_id, semester)

<<<<<<< Updated upstream
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
=======
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
>>>>>>> Stashed changes

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

# ====== Transaction API ======
class createTransactionReq(BaseModel):
    customerID: int
    tuitionID: int

@app.post("/createtransaction")
def createTransaction(createTransReq: createTransactionReq, db = Depends(get_db)):
    conn = get_connection()
    try:
        cur = conn.cursor()

        # Kiểm tra transaction hiện có cho TuitionID
        cur.execute("""
            SELECT TransactionID, CustomerID, `Status`
            FROM `Transaction`
            WHERE TuitionID = %s
            ORDER BY TransactionID DESC
            LIMIT 1
        """, (createTransReq.tuitionID,))
        existing_tx = cur.fetchone()

        # Nếu đã có transaction
        if existing_tx:
            status = existing_tx["Status"]

            if status == "PAID":
                return {"message": "Tuition already paid. Cannot create new transaction."}

            elif (status == "CANCELLED") or (status == "UNPAID"):
                # Cập nhật transaction bị hủy thành pending + đổi CustomerID
                cur.execute("""
                    UPDATE `Transaction`
                    SET CustomerID = %s, `Status` = 'PENDING'
                    WHERE TransactionID = %s
                """, (createTransReq.customerID, existing_tx["TransactionID"]))
                conn.commit()
                return {"message": "Existing cancelled transaction reactivated (pending)."}

            elif status == "PENDING":
                return {"message": "Transaction already pending for this tuition."}

        # Nếu chưa có transaction → tạo mới
        cur.execute("""
            INSERT INTO `Transaction` (CustomerID, TuitionID, `Status`)
            VALUES (%s, %s, 'PENDING')
        """, (createTransReq.customerID, createTransReq.tuitionID))
        conn.commit()

        return {"message": "New transaction created successfully."}

    finally:
        conn.close()


# ====== OTP API ======


def generate_otp():
    return str(random.randint(100000,999999))

<<<<<<< Updated upstream
def send_email(email, otp):
    return 0
    # Code gửi mã otp qua email
=======

def send_otp_email(email, otp):
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
    OTP này sẽ hết hạn sau 5 phút.

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
>>>>>>> Stashed changes

class sendOTPReq(BaseModel):
    customer_id: int
    transaction_id: int
    tuition_id: int
    email: EmailStr

class VerifyOTPReq(BaseModel):
    customer_id: int
    transaction_id: int
    tuition_id: int
    email: EmailStr
    otp: str


@app.post("/sendotp")
def sendOTP(requestOTP: sendOTPReq = Body(...)):
    otp_code = generate_otp()
<<<<<<< Updated upstream
    ttl_seconds = 300  #expire in 5 mins
=======
    ttl_seconds = 160  #expire in 5 mins
    key = str(requestOTP.customer_id) + ":" + str(requestOTP.transaction_id) + ":" + str(requestOTP.tuition_id)
    r = get_redis_connection()
    
    r.setex(key, ttl_seconds, otp_code)
>>>>>>> Stashed changes

    send_otp_email(requestOTP.email, otp_code)

    return {"message": "OTP created & sent successfully"}

@app.post("/verifyotp")
def verifyOTP(requestOTP: VerifyOTPReq = Body(...)):
    key = str(requestOTP.customer_id) + ":" + str(requestOTP.transaction_id) + ":" + str(requestOTP.tuition_id)
    
    
    r = get_redis_connection()
    otp_stored = r.get(key)
    otp_stored = otp_stored if otp_stored else None

    if not otp_stored:
        raise HTTPException(status_code=404, detail="OTP expired or not found")
    
    if otp_stored != requestOTP.otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")
    
    conn = get_connection()
    try:
        cur = conn.cursor(pymysql.cursors.DictCursor)
        cur.execute("SELECT * FROM Tuition INNER JOIN `Transaction` ON Tuition.TuitionID=`Transaction`.TuitionID WHERE `Transaction`.TransactionID=%s", (requestOTP.transaction_id,))

        tuition = cur.fetchone()
        fee = tuition["Fee"]
        cur.execute("UPDATE Customer SET Balance=Balance-%s WHERE CustomerID=%s", (fee, requestOTP.customer_id,))
        cur.execute("UPDATE `Transaction` SET `Status`=\"PAID\" WHERE TransactionID=%s", (requestOTP.transaction_id,))
        conn.commit()
        r.delete(key)
        return {"message": "OTP verified successfully"}
    except Exception as e:
        print("ERROR:", e)
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

