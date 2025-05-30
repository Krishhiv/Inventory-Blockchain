from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from datetime import datetime, timedelta
from auth_utils import verify_password, generate_otp, send_otp_email
from jose import JWTError, jwt
import json
from pathlib import Path
# Bm2g0AcdHb_yXsLq8A-JT_To67eVeoO4My9SUoVWsBekjqfiz2HKXksI7zOOVr0RWSvETDdS-XWsHecoFSSrTQ
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

USERS_FILE = Path("employees.json")
SECRET_KEY = "Bm2g0AcdHb_yXsLq8A-JT_To67eVeoO4My9SUoVWsBekjqfiz2HKXksI7zOOVr0RWSvETDdS-XWsHecoFSSrTQ"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def load_users():
    if USERS_FILE.exists():
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        return email
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

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

    # Generate JWT token
    access_token = create_access_token(data={"sub": data.email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/dashboard")
def dashboard(email: str = Depends(get_current_user)):
    return {"message": f"Welcome {email} to your dashboard"}