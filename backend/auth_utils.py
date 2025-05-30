import random
import smtplib, ssl
from email.message import EmailMessage
from passlib.context import CryptContext

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

# OTP generation
def generate_otp():
    return str(random.randint(100000, 999999))

# Email sender
def send_otp_email(receiver_email, otp):
    msg = EmailMessage()
    msg.set_content(f"Your OTP is: {otp}")
    msg['Subject'] = "Your OTP - Inventory Blockchain"
    msg['From'] = "krishhiv@gmail.com"
    msg['To'] = receiver_email

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login("krishhiv@gmail.com", "aaqb iqbc dmkf emgt")
        server.send_message(msg)
