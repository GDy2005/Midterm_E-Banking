from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from jose import jwt
from db_connection import get_connection

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
def get_userinfo(email: str):
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

# ====== Lấy học phí theo StudentID (liên kết theo Email) ======
def get_tuitioninfo(student_id: int):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM tuition WHERE StudentID=%s", (student_id,))
        tuitions = cur.fetchall()
        return tuitions
    finally:
        conn.close()

# ====== Endpoint ======
@app.get("/tuitioninfo")
def get_tuitioninfo_route(current_user_email: str = Depends(get_current_email)):
    user = get_userinfo(current_user_email)
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