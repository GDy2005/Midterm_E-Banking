from fastapi import FastAPI
from Login import app as login_app
from OTPRequest import app as otp_app
from UserInfo import app as userinfo_app

app = FastAPI()

app.mount("/auth", login_app)   # /auth/login
app.mount("/otp", otp_app)      # /otp/sendotp, /otp/verifyotp
app.mount("/user",userinfo_app) # /user/userinfo