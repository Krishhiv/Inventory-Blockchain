import json
from pathlib import Path
from signatures import Keys

email = input("Please enter your email ID: ")

role = input("Please enter 1 (employee) or 2 (customer): ")
if role == "1":
    role = "employee"
elif role == "2":
    role = "customer"

password = input("Please enter your password: ")

user = Keys(email=email, role=role, password=password)
user.add_to_json()