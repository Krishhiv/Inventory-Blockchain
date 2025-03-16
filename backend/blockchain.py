""" Consider an example of a luxury retail store.
    Each block stores 1 item of the inventory with a unique ID for that item
    Block data: UID, Brand, Item name, Price, Status, Date of Acquirance,   """

import time
import hashlib

class Block:
    def __init__(self, uid, brand, item_name, price, prevHash=""):
        self.uid = uid
        self.brand = brand
        self.item_name = item_name
        self.price = price
        self.timestamp = time.strftime("%d-%m-%Y")
        self.prevHash = prevHash
        self.hash = self.calculate_hash()
        next = None

    
    def calculate_hash(self):
        block_data = (
            str(self.uid) + self.brand + self.item_name + str(self.price) +
            str(self.timestamp) + self.prevHash
        )
        hashed = hashlib.sha256(block_data.encode()).hexdigest()
        return hashed
        
class Blockchain:
    def __init__(self):
        self.head = self.create_genesis_block()
        self.tail = self.head

    def create_genesis_block(self):
        return Block(uid=0, brand="Genesis", item_name="Genesis Block", price=0, prevHash="")
    
    def add_block(self, uid, brand, item_name, price):
        new_block = Block(uid, brand, item_name, price, prevHash=self.tail.hash)
        self.tail.next = new_block
        self.tail = new_block

    def validate_chain(self):
        ptr = self.head
        while ptr.next:
            block_data = (
                str(ptr.uid) + ptr.brand + ptr.item_name + str(ptr.price) +
                str(ptr.timestamp) + ptr.prevHash
            )
            recalculated_hash = hashlib.sha256(block_data.encode()).hexdigest()

            if recalculated_hash != ptr.hash:
                print("ALERT! Blockchain data tampered at block UID:", ptr.uid)
                return False

            if ptr.next.prevHash != ptr.hash:
                print("ALERT! Blockchain linkage broken at block UID:", ptr.uid)
                return False

            ptr = ptr.next

        print("✅ Blockchain is valid and secure.")
        return True


    def print_blockchain(self):
        current = self.head
        while current:
            print(f"\n🔹 Block UID: {current.uid}")
            print(f"   Brand: {current.brand}")
            print(f"   Item Name: {current.item_name}")
            print(f"   Price: ₹{current.price}")
            print(f"   Date: {current.timestamp}")
            print(f"   Previous Hash: {current.prevHash}")
            print(f"   Current Hash: {current.hash}")
            print("-" * 50)
            current = current.next

#Testing
luxury_inventory = Blockchain()
luxury_inventory.add_block(1, "Rolex", "Daytona", 300000)
luxury_inventory.add_block(2, "Louis Vuitton", "Leather Handbag", 250000)
luxury_inventory.add_block(3, "Ferrari", "SF90 Stradale", 55000000)

luxury_inventory.print_blockchain()