import json
from pathlib import Path
from auth_utils import hash_password

USERS_FILE = Path("./backend/employees.json")

def load_users():
    if USERS_FILE.exists():
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)

def add_user(email: str, password: str):
    users = load_users()

    if email in users:
        print(f"❌ User '{email}' already exists.")
        return

    users[email] = {
        "hashed_password": hash_password(password),
        "otp": None,
        "otp_expiry": None
    }

    save_users(users)
    print(f"✅ User '{email}' added successfully.")

if __name__ == "__main__":
    # CHANGE THESE VALUES for different test users
    test_email = input("Enter your email ID: ")
    test_password = input("Enter your password: ")

    add_user(test_email, test_password)
