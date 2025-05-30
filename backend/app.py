from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime, timedelta
from auth_utils import hash_password, verify_password, generate_otp, send_otp_email
import json
from pathlib import Path

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

USERS_FILE = Path("users.json")

def load_users():
    if USERS_FILE.exists():
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)

class LoginRequest(BaseModel):
    email: str
    password: str

class OTPVerifyRequest(BaseModel):
    email: str
    otp: str

@app.post("/login")
def login(data: LoginRequest):
    users = load_users()
    user = users.get(data.email)

    if not user or not verify_password(data.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    otp = generate_otp()
    send_otp_email(data.email, otp)

    user["otp"] = otp
    user["otp_expiry"] = (datetime.utcnow() + timedelta(minutes=5)).isoformat()
    users[data.email] = user
    save_users(users)

    return {"message": "OTP sent to your email"}

@app.post("/verify-otp")
def verify_otp(data: OTPVerifyRequest):
    users = load_users()
    user = users.get(data.email)

    if not user or user["otp"] != data.otp:
        raise HTTPException(status_code=401, detail="Invalid OTP")

    otp_expiry = datetime.fromisoformat(user["otp_expiry"])
    if datetime.utcnow() > otp_expiry:
        raise HTTPException(status_code=401, detail="OTP expired")

    # Invalidate OTP after successful verification
    user["otp"] = None
    user["otp_expiry"] = None
    users[data.email] = user
    save_users(users)

    return {"message": "Login successful!"}
