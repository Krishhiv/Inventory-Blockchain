import time
import hashlib
import json
import os   

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
        self.chains = {}

    def create_genesis_block(self, letter, prev_slot_hash=""):
        """Creates a Genesis block for a given letter slot."""
        return Block(uid=0, brand=f"Genesis-{letter}", item_name="Genesis Block", price=0, prevHash=prev_slot_hash)
    
    def add_block(self, uid, brand, item_name, price):
        """Adds a new block to the correct letter slot."""
        first_letter = brand[0].upper()  # Get the first letter of the brand
        
        if first_letter not in self.chains:
            # If this is the first entry for this letter, create a genesis block
            prev_slot_hash = self.get_last_slot_hash(chr(ord(first_letter) - 1))  # Get hash from previous slot
            self.chains[first_letter] = self.create_genesis_block(first_letter, prev_slot_hash)
        
        # Traverse to the tail of the linked list for this slot
        current = self.chains[first_letter]
        while current.next:
            current = current.next
        
        # Create and link the new block
        new_block = Block(uid, brand, item_name, price, prevHash=current.hash)
        current.next = new_block
        new_block.next = None

    def get_last_slot_hash(self, prev_letter):
        """Gets the last block's hash from the previous letter slot."""
        if prev_letter in self.chains:
            current = self.chains[prev_letter]
            while current.next:
                current = current.next
            return current.hash
        return ""  # Return empty if no previous slot exists
    
    def validate_chain(self):
        """Validates blockchain integrity and linkage for all letter slots."""
        for letter, head in self.chains.items():
            current = head
            while current.next:
                recalculated_hash = current.calculate_hash()
                
                if recalculated_hash != current.hash:
                    print(f"ALERT! Blockchain tampered at block UID: {current.uid} in slot {letter}")
                    return False
                
                if current.next.prevHash != current.hash:
                    print(f"ALERT! Blockchain linkage broken at block UID: {current.uid} in slot {letter}")
                    return False
                
                current = current.next
        
        print("✅ Blockchain is valid and secure.")
        return True
    
    def print_blockchain(self):
        """Prints all blocks grouped by letter slots."""
        for letter, head in self.chains.items():
            print(f"\n🔠 Slot: {letter}")
            current = head
            while current:
                print(f"  🔹 Block UID: {current.uid}, Brand: {current.brand}, Item: {current.item_name}, Price: ₹{current.price}, Status: {current.status}, Hash: {current.hash}")
                current = current.next
            print("-" * 60)

# Example Usage
def main():
    bc = Blockchain()
    bc.add_block(1, "Rolex", "Daytona", 1500000)
    bc.add_block(2, "Rolex", "Submariner", 1200000)
    bc.add_block(3, "Louis Vuitton", "Handbag", 250000)
    bc.add_block(4, "Loro Piana", "Cashmere Jacket", 600000)
    bc.print_blockchain()
    bc.validate_chain()

if __name__ == "__main__":
    main()

