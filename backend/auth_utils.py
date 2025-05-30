import random
import smtplib, ssl
from email.message import EmailMessage
import bcrypt

# Use bcrypt's built-in verification
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())

# OTP generation
def generate_otp():
    return str(random.randint(100000, 999999))

# Send OTP via email
def send_otp_email(receiver_email, otp):
    msg = EmailMessage()
    msg.set_content(f"Your OTP is: {otp}")
    msg['Subject'] = "Your OTP - Inventory Blockchain"
    msg['From'] = "krishhiv@gmail.com"
    msg['To'] = receiver_email

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login("krishhiv@gmail.com", "aaqb iqbc dmkf emgt")  # Replace with secure credentials
        server.send_message(msg)
