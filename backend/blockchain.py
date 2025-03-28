import time
import hashlib
import threading
import queue

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
        block_data = (
            str(self.uid) + self.brand + self.item_name + str(self.price) +
            self.status + str(self.timestamp) + self.prevHash
        )
        return hashlib.sha256(block_data.encode()).hexdigest()

class Blockchain:
    def __init__(self):
        self.chains = {}
        self.pending_blocks = queue.Queue()
        self.initialize_genesis_blocks()
        self.start_verification_thread()

    def initialize_genesis_blocks(self):
        prev_hash = ""  # First genesis block has empty prevHash
        
        # Create genesis blocks for each letter A-Z
        for letter in (chr(i) for i in range(ord('A'), ord('Z') + 1)):
            # Create the genesis block with previous hash
            genesis_block = Block(uid=0, brand=f"Genesis-{letter}", item_name="Genesis Block", price=0, prevHash=prev_hash)
            self.chains[letter] = genesis_block
            
            # Update prev_hash for the next letter's genesis block
            prev_hash = genesis_block.hash

    def add_block(self, uid, brand, item_name, price, status="Available"):
        first_letter = brand[0].upper()
        # Get the last block hash for the chain this block will be added to
        prev_hash = self.get_last_block_hash(first_letter)
        new_block = Block(uid, brand, item_name, price, status, prevHash=prev_hash)
        self.pending_blocks.put(new_block)

    def get_last_block_hash(self, letter):
        if letter and letter in self.chains:
            current = self.chains[letter]
            while current.next:
                current = current.next
            return current.hash
        
        # If the letter doesn't exist or is before 'A', return an empty string
        if letter < 'A':
            return ""
            
        # If the letter is higher than 'A', get the last block of the previous letter
        prev_letter = chr(ord(letter) - 1)
        while prev_letter >= 'A' and prev_letter not in self.chains:
            prev_letter = chr(ord(prev_letter) - 1)
            
        if prev_letter >= 'A':
            return self.get_last_block_hash(prev_letter)
            
        return ""  # Default case

    def verify_and_add_blocks(self):
        while True:
            time.sleep(2)  # Reduce delay for faster validation
            while not self.pending_blocks.empty():
                block = self.pending_blocks.get()
                if self.verify_block(block):
                    self.commit_block(block)

    def verify_block(self, block):
        return block.hash == block.calculate_hash()

    def commit_block(self, block):
        first_letter = block.brand[0].upper()
        current = self.chains[first_letter]

        # Traverse to the last block in the chain
        while current.next:
            current = current.next

        # Ensure correct linking before adding
        block.prevHash = current.hash
        block.hash = block.calculate_hash()  # Recalculate hash after updating prevHash
        current.next = block  

        # After adding the block, update the prevHash of genesis blocks of all subsequent letters
        self.update_subsequent_prev_hashes(first_letter)

    def update_subsequent_prev_hashes(self, starting_letter):
        """
        Updates the prevHash of the genesis block of each subsequent letter's chain
        and recalculates their hashes.
        """
        # Start from the letter after the one where the block was added
        current_letter = starting_letter
        prev_last_block_hash = self.get_last_block_hash(current_letter)

        # Iterate over all subsequent letters
        next_letter = chr(ord(current_letter) + 1)
        while next_letter <= 'Z':
            if next_letter in self.chains:
                # Update the prevHash of the genesis block of the next letter
                next_genesis_block = self.chains[next_letter]
                next_genesis_block.prevHash = prev_last_block_hash
                # Recalculate the hash of the genesis block since prevHash changed
                next_genesis_block.hash = next_genesis_block.calculate_hash()
                # Update the prev_last_block_hash for the next iteration
                prev_last_block_hash = self.get_last_block_hash(next_letter)
            next_letter = chr(ord(next_letter) + 1)

    def validate_chain(self):
        """ Validates entire blockchain integrity by checking previous hashes """
        # First validate the linkage from A-Z across letters
        prev_last_block_hash = ""  # Start with empty hash
        
        for letter in sorted(self.chains.keys()):
            # Get the genesis block for this letter
            genesis_block = self.chains[letter]
            
            # The genesis block's prevHash should match the last block of previous letter
            # (except for A, which has empty prevHash)
            if letter > 'A':
                if genesis_block.prevHash != prev_last_block_hash:
                    print(f"❌ Chain link broken between letter {chr(ord(letter) - 1)} and {letter}")
                    print(f"Expected prevHash: {prev_last_block_hash}")
                    print(f"Found: {genesis_block.prevHash}")
                    return False
            elif letter == 'A' and genesis_block.prevHash != "":
                print("❌ Genesis block A should have empty prevHash")
                return False
                
            # Now validate each block in this letter's chain
            current = genesis_block
            prev_hash = prev_last_block_hash if letter > 'A' else ""
            
            while current:
                # Verify the prevHash linkage
                if current.prevHash != prev_hash:
                    print(f"❌ Block linkage broken at {current.brand} - UID: {current.uid}")
                    print(f"Expected prevHash: {prev_hash}")
                    print(f"Found: {current.prevHash}")
                    return False
                    
                # Verify the hash integrity
                calculated_hash = current.calculate_hash()
                if current.hash != calculated_hash:
                    print(f"❌ Hash mismatch at {current.brand} - UID: {current.uid}")
                    print(f"Expected hash: {calculated_hash}")
                    print(f"Found: {current.hash}")
                    return False
                
                # Move to next block
                prev_hash = current.hash
                current = current.next
            
            # Remember the last block hash for this letter - will be needed for next letter
            last_block = genesis_block
            while last_block.next:
                last_block = last_block.next
            
            prev_last_block_hash = last_block.hash
        
        print("✅ Blockchain is valid!")
        return True
    
    def start_verification_thread(self):
        thread = threading.Thread(target=self.verify_and_add_blocks, daemon=True)
        thread.start()

    def print_blockchain(self):
        for letter, head in sorted(self.chains.items()):
            print(f"\n🔠 Slot: {letter}")
            current = head
            while current:
                # Truncate hashes for better readability
                prev_hash_display = current.prevHash[:10] + "..." if current.prevHash else ""
                hash_display = current.hash[:10] + "..."
                
                print(f"  🔹 Block UID: {current.uid}, Brand: {current.brand}, Item: {current.item_name}, Price: ₹{current.price}, Status: {current.status}")
                print(f"    Previous Hash: {prev_hash_display}")
                print(f"    Hash: {hash_display}")
                current = current.next
            print("-" * 60)

def main():
    bc = Blockchain()
    
    while True:
        print("\n--- Blockchain Menu ---")
        print("1. Add Block")
        print("2. Print Blockchain")
        print("3. Validate Blockchain")
        print("4. Exit")
        
        choice = input("Enter your choice: ")
        
        if choice == "1":
            uid = int(input("Enter UID: "))
            brand = input("Enter Brand Name: ")
            item_name = input("Enter Item Name: ")
            price = float(input("Enter Price: "))
            status = input("Enter Status (Available/Sold/etc.): ")
            bc.add_block(uid, brand, item_name, price, status)
            print("Block added to pending queue.")
            
        elif choice == "2":
            bc.print_blockchain()
            
        elif choice == "3":
            if bc.validate_chain():
                print("Blockchain is fully linked and valid!")
            else:
                print("Blockchain is broken!")
            
        elif choice == "4":
            print("Exiting...")
            break
        
        else:
            print("Invalid choice. Please try again.")
        
        # Give the verification thread some time to process pending blocks
        time.sleep(3)

if __name__ == "__main__":
    main()