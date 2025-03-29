import json
import getpass
import base64
import os
import hashlib
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from blspy import PrivateKey, G1Element

BLS_GROUP_ORDER = 0x73eda753299d7d483339d80809a1d80553bda402fffe5bfeffffffff00000001

class Keys:
    def __init__(self, name, role, password):
        self.name = name
        self.role = role
        self.salt = os.urandom(16)  # Generate a random salt
        self.nonce = os.urandom(12)  # Generate a random nonce for AES-GCM
        self.hashed_password = self.hash_password(password, self.salt)  # Hash password
        self.encryption_key = self.derive_key(password, self.salt)  # Derive encryption key
        self.private_key, self.public_key = self.generate_bls_keys(password)  # Generate BLS keys
        self.encrypted_private_key = self.encrypt_private_key()  # Encrypt private key

    def hash_password(self, password, salt):
        """Hashes a password using SHA-256 with a salt."""
        return hashlib.sha256(salt + password.encode()).digest()

    def derive_key(self, password, salt):
        """Derives an AES encryption key from a password using PBKDF2."""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        return kdf.derive(password.encode())

    def generate_bls_keys(self, password):
        """Generates a BLS private-public key pair securely from a hashed password."""
        hashed_password = hashlib.sha256(password.encode()).digest()
        int_sk = int.from_bytes(hashed_password, "big") % BLS_GROUP_ORDER
        private_key_bytes = int_sk.to_bytes(32, "big")
        private_key = PrivateKey.from_bytes(private_key_bytes)
        public_key = private_key.get_g1()
        return bytes(private_key), bytes(public_key)

    def encrypt_private_key(self):
        """Encrypts the private key using AES-GCM."""
        cipher = Cipher(algorithms.AES(self.encryption_key), modes.GCM(self.nonce))
        encryptor = cipher.encryptor()
        encrypted_private_key = encryptor.update(self.private_key) + encryptor.finalize()
        tag = encryptor.tag
        return base64.b64encode(self.nonce + tag + encrypted_private_key).decode()

    def add_to_json(self):
        """Stores user data securely in a JSON file."""
        filename = f"{self.role}s.json"
        data_entry = {
            "name": self.name,
            "hashed_password": base64.b64encode(self.hashed_password).decode(),
            "public_key": base64.b64encode(self.public_key).decode(),
            "encrypted_private_key": self.encrypted_private_key,  # Already a Base64 string
            "salt": base64.b64encode(self.salt).decode(),
        }
        try:
            with open(filename, "r") as file:
                data = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            data = []
        data.append(data_entry)
        with open(filename, "w") as file:
            json.dump(data, file, indent=4)

    @staticmethod
    def authenticate_and_decrypt(name, role, input_password):
        """Authenticates a user and decrypts their private key if credentials match."""
        filename = f"{role}s.json"
        try:
            with open(filename, "r") as file:
                users = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            print("No registered users found.")
            return None
        for user in users:
            if user["name"] == name:
                stored_hashed_password = base64.b64decode(user["hashed_password"])
                salt = base64.b64decode(user["salt"])
                encrypted_data = base64.b64decode(user["encrypted_private_key"])
                nonce, tag, ciphertext = encrypted_data[:12], encrypted_data[12:28], encrypted_data[28:]
                
                # Verify password
                input_hashed_password = hashlib.sha256(salt + input_password.encode()).digest()
                if input_hashed_password == stored_hashed_password:
                    print("\n✅ Password correct! Now verifying 2FA...")
                    otp = input("Enter the 6-digit 2FA code: ")
                    if otp != "123456":
                        print("❌ 2FA verification failed!")
                        return None
                    encryption_key = Keys.derive_key_static(input_password, salt)
                    cipher = Cipher(algorithms.AES(encryption_key), modes.GCM(nonce, tag))
                    decryptor = cipher.decryptor()
                    private_key = decryptor.update(ciphertext) + decryptor.finalize()
                    print("\n🔓 Private Key Successfully Retrieved!")
                    return private_key.hex()
                else:
                    print("❌ Incorrect password!")
                    return None
        print("❌ User not found!")
        return None

    @staticmethod
    def derive_key_static(password, salt):
        """Static method to derive encryption key."""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        return kdf.derive(password.encode())


# ================================
# 🌟 Menu-Based `main()` Function
# ================================
def main():
    while True:
        print("\n🔐 Secure Key Management System")
        print("1️⃣ Register (New Employee/Customer)")
        print("2️⃣ Authenticate & Retrieve Private Key")
        print("3️⃣ Exit")
        choice = input("\nEnter your choice: ")

        if choice == "1":
            name = input("Enter your name: ")
            role = input("Are you an employee or customer? ").lower()

            if role not in ["employee", "customer"]:
                print("❌ Invalid role! Please enter 'employee' or 'customer'.")
                continue

            password = getpass.getpass("Enter a secure password: ")
            user = Keys(name, role, password)
            user.add_to_json()

            print("\n✅ User successfully registered! Your keys are stored securely.")

        elif choice == "2":
            name = input("Enter your name: ")
            role = input("Are you an employee or customer? ").lower()

            if role not in ["employee", "customer"]:
                print("❌ Invalid role! Please enter 'employee' or 'customer'.")
                continue

            password = getpass.getpass("Enter your password: ")
            private_key = Keys.authenticate_and_decrypt(name, role, password)

            if private_key:
                print(f"\n🔑 Your Private Key: {private_key}")

        elif choice == "3":
            print("\n👋 Exiting Secure Key Management System. Stay Safe!")
            break

        else:
            print("❌ Invalid choice! Please enter 1, 2, or 3.")

# Run the program
if __name__ == "__main__":
    main()
