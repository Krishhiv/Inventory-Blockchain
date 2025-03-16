import time
import hashlib
from security import sign_transaction, verify_transaction, generate_keys_for_customer, generate_company_keys

# ✅ Ensure company keys exist before blockchain starts
generate_company_keys()  # 🔹 FIX: Prevents FileNotFoundError for 'private_key.pem'

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

    def execute_sale(self, uid, customer_name):
        """Handles the secure sale process of an item."""
        ptr = self.head
        while ptr:
            if ptr.uid == uid and ptr.status == "Available":
                transaction_data = f"Sale of {ptr.brand} {ptr.item_name} for ₹{ptr.price}"

                # ✅ Ensure customer keys exist
                generate_keys_for_customer(customer_name)
                customer_pub_key = f"{customer_name}_public.pem"

                # ✅ Ensure company keys exist
                generate_company_keys()  # 🔹 FIX: This ensures 'private_key.pem' exists before signing

                # ✅ Sign transaction (Company & Customer)
                company_signature = sign_transaction(transaction_data, "private_key.pem")
                customer_signature = sign_transaction(transaction_data, f"{customer_name}_private.pem")

                # ✅ Verify and execute sale
                if verify_transaction(transaction_data, [company_signature, customer_signature], ["public_key.pem", customer_pub_key]):
                    ptr.status = "Sold"  # ✅ Update block status
                    print(f"✅ Sale executed: {ptr.brand} {ptr.item_name} is now SOLD.")
                    self.rehash_chain()
                    return True
                else:
                    print("❌ ERROR: Sale verification failed.")
                    return False
            ptr = ptr.next

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
                print("⚠️ ALERT! Blockchain data tampered at block UID:", ptr.uid)
                return False

            # ✅ Check blockchain linkage
            if ptr.next.prevHash != ptr.hash:
                print("⚠️ ALERT! Blockchain linkage broken at block UID:", ptr.uid)
                return False

            ptr = ptr.next

        print("✅ Blockchain is valid and secure.")
        return True

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

# ✅ Run Tests
if __name__ == "__main__":
    luxury_inventory = Blockchain()
    luxury_inventory.add_block(1, "Rolex", "Daytona", 300000)
    luxury_inventory.add_block(2, "Louis Vuitton", "Leather Handbag", 250000)
    luxury_inventory.add_block(3, "Ferrari", "SF90 Stradale", 55000000)

    # ✅ Print Initial Blockchain
    luxury_inventory.print_blockchain()

    # ✅ Execute Sale
    luxury_inventory.execute_sale(1, "JohnDoe")

    # ✅ Print Updated Blockchain
    luxury_inventory.print_blockchain()
