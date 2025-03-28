from blspy import BasicSchemeMPL #type: ignore
import hashlib
import os
import json 

class SecurityProfile:
    def __init__(self, name, role):
        self.name = name
        self.role = role
        self.password = input("Enter a secure password (you will not be allowed to see it again): ")
        self.private_key, self.public_key = self.generate_keys()
        self.add_to_json()

    def generate_keys(self):
        self.salt = os.urandom(16)
        self.hashed_password = hashlib.sha256(self.password.encode('utf-8')).hexdigest()
        self.seed = hashlib.sha256((self.name + self.role + self.hashed_password + self.salt).encode('utf-8')).digest()
        private_key = BasicSchemeMPL.key_gen(self.seed)
        public_key = private_key.get_g1()
        return private_key, public_key

    def add_to_json(self):
        if self.role == 'auditor':
            print("Cannot modify this.")
            return

        with open(f'./backend/profiles/{self.role}.json', 'r') as f:
            data = json.load(f)
            data.append({
                'name': self.name,
                'private_key': self.private_key,
                'hashed_password': self.hashed_password,
                'public_key': self.public_key
            })
        with open(f'./backend/profiles/{self.role}.json', 'w') as f:
            json.dump(data, f, indent=4)
        print(f"Added {self.name}'s data to {self.role} profiles.")

        with open('./backend/profiles/auditor.json', 'r'):
            data = json.load(f)
            if data is not None:
                data['audit_key'] = data['audit_key'] + self.public_key
            else:
                data['audit_key'] = self.public_key
        with open('./backend/profiles/auditor.json', 'w') as f:
            json.dump(data, f, indent=4)
        print(f"Added {self.name}'s public key to auditor profiles.")

        return

class Signing:
    pass

class Auditing:
    pass

if "name" == "__main__":
    krishhiv = SecurityProfile("Krishhiv", "employee")
