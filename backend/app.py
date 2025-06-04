from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from datetime import datetime, timedelta
from auth_utils import verify_password, generate_otp, send_otp_email
from jose import JWTError, jwt
import json
import base64
from signatures import Keys
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

EMPS_FILE = Path("employees.json")
CUSTOMERS_FILE = Path("customers.json")
SECRET_KEY = "Bm2g0AcdHb_yXsLq8A-JT_To67eVeoO4My9SUoVWsBekjqfiz2HKXksI7zOOVr0RWSvETDdS-XWsHecoFSSrTQ"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def load_emps():
    if EMPS_FILE.exists():
        with open(EMPS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_emps(users):
    with open(EMPS_FILE, "w") as f:
        json.dump(users, f, indent=2)

def load_customers():
    if CUSTOMERS_FILE.exists():
        try:
            with open(CUSTOMERS_FILE, "r") as f:
                content = f.read().strip()
                return json.loads(content) if content else {}
        except json.JSONDecodeError:
            return {}  # fallback if file is invalid
    return {}


def save_customers(customers):
    with open(CUSTOMERS_FILE, "w") as f:
        json.dump(customers, f, indent=2)


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

@app.post("/emp-login")
def login(data: LoginRequest):
    users = load_emps()
    user = users.get(data.email)

    if not user or not verify_password(data.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    otp = generate_otp()
    send_otp_email(data.email, otp)

    user["otp"] = otp
    user["otp_expiry"] = (datetime.utcnow() + timedelta(minutes=5)).isoformat()
    users[data.email] = user
    save_emps(users)

    return {"message": "OTP sent to your email"}

@app.post("/verify-emp-otp")
def verify_otp(data: OTPVerifyRequest):
    users = load_emps()
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
    save_emps(users)

    # Generate JWT token
    access_token = create_access_token(data={"sub": data.email})
    return {"access_token": access_token, "token_type": "bearer"}

class CustomerRegisterRequest(BaseModel):
    email: str
    password: str
    otp: str

@app.post("/register-customer")
def register_customer(data: CustomerRegisterRequest):
    customers = load_customers()
    record = customers.get(data.email)

    if not record or record.get("otp") != data.otp:
        raise HTTPException(status_code=401, detail="Invalid OTP")

    otp_expiry_str = record.get("otp_expiry", "")
    if not otp_expiry_str:
        raise HTTPException(status_code=401, detail="Missing OTP expiry")
    otp_expiry = datetime.fromisoformat(otp_expiry_str)
    if datetime.utcnow() > otp_expiry:
        raise HTTPException(status_code=401, detail="OTP expired")

    # Generate keys and secure data
    user = Keys(email=data.email, role="customer", password=data.password)
    user.add_to_json()

    # Finalize customer record (convert all to JSON-safe types)
    customers[data.email] = {
        "email": data.email,
        "role": "customer",
        "public_key": base64.b64encode(user.public_key).decode("utf-8") if isinstance(user.public_key, bytes) else user.public_key,
        "encrypted_private_key": user.encrypted_private_key,  # already a string
        "salt": user.salt.decode("utf-8") if isinstance(user.salt, bytes) else user.salt,
        "hashed_password": user.hashed_password.decode("utf-8") if isinstance(user.hashed_password, bytes) else user.hashed_password,
        "otp": None,
        "otp_expiry": None,
    }

    save_customers(customers)
    return {"message": "Customer account created successfully"}

class EmailRequest(BaseModel):
    email: str

@app.post("/customer-send-otp")
def customer_send_otp(data: EmailRequest):
    customers = load_customers()

    if data.email in customers:
        raise HTTPException(status_code=400, detail="Customer already exists")

    otp = generate_otp()
    send_otp_email(data.email, otp)

    customers[data.email] = {
        "otp": otp,
        "otp_expiry": (datetime.utcnow() + timedelta(minutes=5)).isoformat()
    }
    save_customers(customers)
    return {"message": "OTP sent to customer email"}

@app.get("/dashboard")
def dashboard(email: str = Depends(get_current_user)):
    return {"message": f"Welcome {email} to your dashboard"}