from fastapi import FastAPI
from backend.Login import app as login_app
from backend.OTPRequest import app as otp_app
from backend.UserInfo import app as userinfo_app
from backend.StudentInfo import app as studentinfo_app

app = FastAPI()

app.mount("/auth", login_app)   # /auth/login

# ========= Login API =========

app.mount("/otp", otp_app)      # /otp/sendotp, /otp/verifyotp
app.mount("/user",userinfo_app) # /user/userinfo
app.mount("/student", studentinfo_app) #/student/studentinfo