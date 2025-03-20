import time
import hashlib
import rsa
import json

class SecurityProfile:
    def __init__(self, type, name):
        self.type = type # 'employee' or 'customer' or 'auditor'
        self.name = name
        (self.public_id, self.private_id) = rsa.newkeys(512)
        if self.type == 'employee':
            self.save_to_employee_json()
        elif self.type == 'customer':
            self.save_to_customer_json()
        else:
            self.save_to_auditor_json()

    def save_to_customer_json(self):
        data = {
            "type": self.type,
            "name": self.name,
            "public_id": self.public_id.save_pkcs1().decode(),  # Convert public key to PEM format
            "private_id": self.private_id.save_pkcs1().decode()  # Convert private key to PEM format
        }

        with open('./backend/customers.json', 'w') as f:
            json.dump(data, f, indent=4)

        print(f"Saved {self.name}'s data into customers.json")

    def save_to_employee_json(self):
        data = {
            "type": self.type,
            "name": self.name,
            "public_id": self.public_id.save_pkcs1().decode(),  # Convert public key to PEM format
            "private_id": self.private_id.save_pkcs1().decode()  # Convert private key to PEM format
        }

        with open('./backend/employees.json', 'w') as f:
            json.dump(data, f, indent=4)

        print(f"Saved {self.name}'s data into employees.json")

    def save_to_auditor_json(self):
        data = {
            "type": self.type,
            "name": self.name,
            "public_id": self.public_id.save_pkcs1().decode(),  # Convert public key to PEM format
            "private_id": self.private_id.save_pkcs1().decode()  # Convert private key to PEM format
        }

        with open('./backend/auditors.json', 'w') as f:
            json.dump(data, f, indent=4)

        print(f"Saved {self.name}'s data into auditors.json")    

    def add_profile(self, type, name):
        new_profile = SecurityProfile(type, name)
        return

class Block:
    def __init__(self, uid, brand, item_name, price, status="Available", prevHash=""):
        self.uid = uid
        self.brand = brand
        self.item_name = item_name
        self.price = price
        self.status = status
        self.timestamp = time.strftime("%d-%m-%Y")
        self.prevHash = prevHash
        self.hash = self.calculate_hash()
        self.next = None  

    def calculate_hash(self):
        """Generates SHA-256 hash of the block (including status)."""
        block_data = (
            str(self.uid) + self.brand + self.item_name + str(self.price) +
            self.status + str(self.timestamp) + self.prevHash
        )
        return hashlib.sha256(block_data.encode()).hexdigest()

class Blockchain:
    def __init__(self):
        self.head = self.create_genesis_block()
        self.tail = self.head

    def create_genesis_block(self):
        """Creates the first block in the blockchain."""
        return Block(uid=0, brand="Genesis", item_name="Genesis Block", price=0, prevHash="")

    def add_block(self, uid, brand, item_name, price):
        """Adds a new block to the blockchain."""
        new_block = Block(uid, brand, item_name, price, prevHash=self.tail.hash)
        self.tail.next = new_block
        self.tail = new_block

    def rehash_chain(self):
        ptr = self.head
        while ptr:
            # Store the next block (if it exists) before updating the current block's hash
            next_block = ptr.next
            # Recalculate the current block's hash
            ptr.hash = ptr.calculate_hash()
            # If there’s a next block, update its prevHash to the current block’s new hash
            if next_block:
                next_block.prevHash = ptr.hash
            ptr = ptr.next
        print("✅ Blockchain re-hashed successfully.")

    def validate_chain(self):
        """Validates blockchain integrity and linkage."""
        ptr = self.head
        while ptr.next:
            recalculated_hash = ptr.calculate_hash()

            # ✅ Check block integrity
            if recalculated_hash != ptr.hash:
                print("ALERT! Blockchain data tampered at block UID:", ptr.uid)
                return False

            # ✅ Check blockchain linkage
            if ptr.next.prevHash != ptr.hash:
                print("ALERT! Blockchain linkage broken at block UID:", ptr.uid)
                return False

            ptr = ptr.next

        print("✅ Blockchain is valid and secure.")
        return True
    
    def execute_sale(self, item, employee_name, customer_name):
        # Searching for employee and customer in the .json files and extracting their corresponding objects.
        with open('./backend/employees.json', 'r') as f:
            employees = json.load(f)
        
        for employee in employees:
            if employee.get('name') == employee_name:
                break
        
        with open('./backend/customers.json', 'r') as f:
            customers = json.load(f)

        for customer in customers:
            if customer.get('name') == customer_name:
                break

        # Searching for the block of the item for which the sale is happening
        ptr = self.head
        while ptr:
            if ptr.item_name == item:
                """ Write full sale execution logic here """
                pass

    def print_blockchain(self):
        """Traverses and prints all blocks in the blockchain."""
        current = self.head
        while current:
            print(f"\n🔹 Block UID: {current.uid}")
            print(f"   Brand: {current.brand}")
            print(f"   Item Name: {current.item_name}")
            print(f"   Price: ₹{current.price}")
            print(f"   Date: {current.timestamp}")
            print(f"   Status: {current.status}")
            print(f"   Previous Hash: {current.prevHash}")
            print(f"   Current Hash: {current.hash}")
            print("-" * 50)
            current = current.next

# Run Tests
if __name__ == "__main__":
    diya_basu = SecurityProfile('auditor', 'Diya Basu')
    krishhiv_mehra = SecurityProfile('employee', 'Krishhiv Mehra')
    virat_kohli = SecurityProfile('customer', 'Virat Kohli')
