from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from backend.db_connection import get_connection
from jose import jwt

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

# ====== Endpoint ======
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
