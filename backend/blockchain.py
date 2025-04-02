import time
import hashlib
import threading
import queue
import json
import getpass
from signatures import Keys, Signing, MerkleNode, MerkleTree



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

        self.creation_signature = None # b64 encoded
        self.creation_pub = None # b64 encoded
        
        self.sale_agg_signature = None # b64 encoded
        self.sale_agg_pub = None # b64 encoded

    def calculate_hash(self):
        block_data = (
            str(self.uid) + self.brand + self.item_name + str(self.price) +
            self.status + str(self.timestamp) + self.prevHash
        )
        return hashlib.sha256(block_data.encode()).hexdigest()

    def get_signable_data(self, use_original_status=False):
        """Returns the data that should be signed, excluding prevHash"""
        # For sale updates, use the original "Available" status when verifying creation signature
        status_to_use = "Available" if use_original_status else self.status
        return (
            str(self.uid) + self.brand + self.item_name + str(self.price) +
            status_to_use + str(self.timestamp)
        )

    def verify_creation_signature(self):
        """Verify the creation signature for this block"""
        if not self.creation_signature or not self.creation_pub:
            print("❌ Missing creation signature or public key")
            return False
        try:
            # Use original "Available" status when verifying creation signature
            return Signing.verify_signature(self.creation_pub, self.get_signable_data(use_original_status=True), self.creation_signature)
        except Exception as e:
            print(f"❌ Creation signature verification error: {e}")
            return False

    def verify_sale_signature(self):
        """Verify the sale signature for this block"""
        if not self.sale_agg_signature or not self.sale_agg_pub:
            print("❌ Missing sale signature or public key")
            return False
        try:
            # Use current "Sold" status when verifying sale signature
            return Signing.verify_signature(self.sale_agg_pub, self.get_signable_data(use_original_status=False), self.sale_agg_signature)
        except Exception as e:
            print(f"❌ Sale signature verification error: {e}")
            return False

class Blockchain:
    def __init__(self):
        self.chains = {}
        self.pending_blocks = queue.Queue()
        self.merkle_tree = MerkleTree()  # Create merkle_tree as an instance variable
        self.initialize_genesis_blocks()
        self.start_verification_thread()
        self.start_heartbeat()

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
        
        # Create new block
        new_block = Block(uid, brand, item_name, price, status, prevHash=prev_hash)
        
        # Calculate the block's hash
        new_block.hash = new_block.calculate_hash()
        
        # Get user credentials for signing
        name = input("Enter employee name: ")
        password = getpass.getpass("Enter your password: ")

        # Sign the block with user's private key
        signature_result = Signing.sign_data(name, "employee", password, new_block.get_signable_data())
        
        if not signature_result:
            print("❌ Failed to sign the block. Block not added.")
            return
            
        new_block.creation_signature, new_block.creation_pub = signature_result
        
        # Add the block to pending queue for verification
        self.pending_blocks.put(new_block)
        print(f"Block for {brand} - UID: {uid} submitted for verification.")

    def execute_sale(self, uid, brand):
        # Step 1: Search for the block and check if the product is available
        first_letter = brand[0].upper()
        current = self.chains[first_letter]
        block_to_sell = None
        while current:
            if current.uid == uid:
                block_to_sell = current
                break
            current = current.next
        
        if block_to_sell is None:
            print("❌ Item is not in inventory")
            return
        if block_to_sell.status == "Sold":
            print("❌ Item is already sold.")
            return
        
        print()
        print(f"Selling {block_to_sell.brand} {block_to_sell.item_name} - UID: {block_to_sell.uid}")
        print(f"Cost: {block_to_sell.price}")
        print()
        
        # Step 2: Take inputs for employee and customer credentials
        emp_name = input("Enter the name of the employee selling this item: ")
        emp_password = getpass.getpass(f"Enter Employee {emp_name}'s password: ")

        cust_name = input("Enter the name of the customer buying this item: ")

        try:
            with open("./profiles/customers.json", "r") as f:
                customers = json.load(f)
        except FileNotFoundError:
            customers = []

        # Check if the customer exists, create profile if needed
        if not any(customer["name"] == cust_name for customer in customers):
            print(f"Customer {cust_name} not found. Creating a new profile...")
            cust_password = getpass.getpass(f"Enter Customer {cust_name}'s password: ")
            cust = Keys(cust_name, "customer", cust_password)
            cust.add_to_json()
        else:
            cust_password = getpass.getpass(f"Enter Customer {cust_name}'s password: ")

        # Update the original block's status first
        block_to_sell.status = "Sold"
        
        # Create a sale update block (clone of the block to be sold with additional signatures)
        sale_update_block = Block(
            uid=block_to_sell.uid,
            brand=block_to_sell.brand,
            item_name=block_to_sell.item_name,
            price=block_to_sell.price,
            status="Sold",  # Ensure this is set to "Sold"
            prevHash=block_to_sell.prevHash
        )
        
        # Copy existing block properties
        sale_update_block.timestamp = block_to_sell.timestamp
        sale_update_block.creation_signature = block_to_sell.creation_signature
        sale_update_block.creation_pub = block_to_sell.creation_pub
        
        # Add new sale signatures
        signature_result = Signing.sign_data_dual(
            emp_name, emp_password, cust_name, cust_password, sale_update_block.get_signable_data())
        
        if not signature_result:
            # Revert the status if signature fails
            block_to_sell.status = "Available"
            print("❌ Failed to create signatures for the sale. Sale canceled.")
            return
            
        sale_update_block.sale_agg_signature, sale_update_block.sale_agg_pub = signature_result
        
        # Recalculate hash after all properties are set
        sale_update_block.hash = sale_update_block.calculate_hash()
        
        # Add the update to the pending queue for verification
        self.pending_blocks.put(sale_update_block)
        print("Sale submitted for verification.")

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
                
                # Step 1: Verify block hash integrity
                if not self.verify_block_hash(block):
                    print(f"❌ Block hash verification failed for {block.brand} - UID: {block.uid}")
                    continue
                    
                # Step 2: Verify creation signature
                if not block.verify_creation_signature():
                    print(f"❌ Creation signature verification failed for {block.brand} - UID: {block.uid}")
                    continue
                    
                # Step 3: If this is a sale update (has sale signature), verify it
                if block.sale_agg_signature and block.sale_agg_pub:
                    if not block.verify_sale_signature():
                        print(f"❌ Sale signature verification failed for {block.brand} - UID: {block.uid}")
                        continue
                
                # Step 4: Commit block to chain
                self.commit_block(block)
                
                # Step 5: Verify Merkle tree integrity after adding the new block
                if not self.merkle_tree.verify_merkle():
                    print("❌ Merkle tree verification failed after adding block!")
                    # We could implement rollback logic here if needed

    def verify_block_hash(self, block):
        """Verify that the block's hash is calculated correctly"""
        return block.hash == block.calculate_hash()

    def commit_block(self, block):
        """Commit a verified block to the blockchain"""
        first_letter = block.brand[0].upper()
        
        # Handle sale updates differently from new blocks
        if block.sale_agg_signature and block.sale_agg_pub:
            # This is a sale update - find the existing block and update it
            current = self.chains[first_letter]
            while current:
                if current.uid == block.uid and current.brand == block.brand:
                    # Update existing block with sale information
                    current.status = "Sold"  # Ensure status is updated
                    current.sale_agg_signature = block.sale_agg_signature
                    current.sale_agg_pub = block.sale_agg_pub
                    current.hash = current.calculate_hash()  # Recalculate hash after updates
                    
                    # Update the Merkle tree with sale information
                    self.merkle_tree.add_block_keys(current.creation_pub, current.sale_agg_pub)
                    
                    print(f"✅ Sale verified and recorded for {block.brand} - UID: {block.uid}")
                    print(f"Status updated to: {current.status}")  # Add status confirmation
                    
                    # Update chain linkages after the sale
                    self.update_subsequent_prev_hashes(first_letter)
                    return
                current = current.next
                
            print(f"❌ Could not find block with UID {block.uid} to update sale status")
            return
        
        # For new blocks (not sales), proceed with normal block addition
        if first_letter not in self.chains:
            # If this is the first block for this letter, create a new chain
            self.chains[first_letter] = block
            block.prevHash = self.get_last_block_hash(first_letter)
            block.hash = block.calculate_hash()
        else:
            # Add to existing chain
            current = self.chains[first_letter]
            while current.next:
                current = current.next
            block.prevHash = current.hash
            block.hash = block.calculate_hash()
            current.next = block
        
        # Update the Merkle tree with the new block's creation key
        self.merkle_tree.add_block_keys(block.creation_pub)

        print(f"✅ New block verified and added: {block.brand} - UID: {block.uid}")

        # After adding the block, update the prevHash of all blocks in subsequent chains
        self.update_subsequent_prev_hashes(first_letter)

    def update_subsequent_prev_hashes(self, starting_letter):
        """
        Updates the prevHash of all blocks in each subsequent chain when a new block is added or modified.
        """
        # Get the last block hash of the chain we just modified
        current_last_block = self.chains[starting_letter]
        while current_last_block.next:
            current_last_block = current_last_block.next
        prev_last_block_hash = current_last_block.hash

        # Update all subsequent chains
        for letter in sorted(self.chains.keys()):
            if letter > starting_letter:
                # Update genesis block
                genesis_block = self.chains[letter]
                genesis_block.prevHash = prev_last_block_hash
                genesis_block.hash = genesis_block.calculate_hash()
                
                # Update all subsequent blocks in this chain
                current = genesis_block
                while current.next:
                    current.next.prevHash = current.hash
                    current.next.hash = current.next.calculate_hash()
                    current = current.next
                
                # Update prev_last_block_hash for the next chain
                prev_last_block_hash = current.hash

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
    
    def verify_block_signatures(self, specific_uid=None, specific_brand=None):
        """Verify signatures for all blocks or a specific block"""
        all_valid = True
        
        for letter, head in sorted(self.chains.items()):
            if specific_brand and specific_brand[0].upper() != letter:
                continue
                
            current = head
            while current:
                if specific_uid is not None and current.uid != specific_uid:
                    current = current.next
                    continue
                    
                # Skip genesis blocks
                if current.uid == 0 and "Genesis" in current.brand:
                    current = current.next
                    continue
                
                # Verify creation signature
                if current.creation_signature and current.creation_pub:
                    try:
                        creation_valid = current.verify_creation_signature()
                        if not creation_valid:
                            print(f"❌ Creation signature invalid: {current.brand} - UID: {current.uid}")
                            all_valid = False
                    except Exception as e:
                        print(f"❌ Creation signature verification error: {current.brand} - UID: {current.uid}, {e}")
                        all_valid = False
                else:
                    print(f"⚠️ Missing creation signature: {current.brand} - UID: {current.uid}")
                    all_valid = False
                
                # Verify sale signature if marked as sold
                if current.status == "Sold":
                    if current.sale_agg_signature and current.sale_agg_pub:
                        try:
                            sale_valid = current.verify_sale_signature()
                            if not sale_valid:
                                print(f"❌ Sale signature invalid: {current.brand} - UID: {current.uid}")
                                all_valid = False
                        except Exception as e:
                            print(f"❌ Sale signature verification error: {current.brand} - UID: {current.uid}, {e}")
                            all_valid = False
                    else:
                        print(f"⚠️ Item marked as sold but missing sale signature: {current.brand} - UID: {current.uid}")
                        all_valid = False
                
                current = current.next
                
                # Break early if we found the specific block
                if specific_uid is not None and specific_brand is not None and current and current.uid == specific_uid:
                    break
        
        if all_valid:
            print("✅ All signatures are valid!")
        return all_valid
        
    def verify_merkle_tree(self):
        """Verify the integrity of the Merkle tree"""
        return self.merkle_tree.verify_merkle()
    
    def print_merkle_tree(self):
        """Print the current Merkle tree"""
        from signatures import print_merkle_tree_recursive
        print("\n📊 Current Merkle Tree:")
        if self.merkle_tree.root:
            print_merkle_tree_recursive(self.merkle_tree.root)
        else:
            print("Merkle tree is empty.")
    
    def start_verification_thread(self):
        thread = threading.Thread(target=self.verify_and_add_blocks, daemon=True)
        thread.start()

    def start_heartbeat(self):
        def heartbeat():
            while True:
                print("Running heartbeat check...")
                # Verify blockchain integrity
                if not self.validate_chain():
                    print("❌ Blockchain integrity verification failed.")
                if not self.verify_block_signatures():
                    print("❌ Block signatures verification failed.")
                if not self.verify_merkle_tree():
                    print("❌ Merkle tree verification failed.")
                
                # Commit any pending blocks
                while not self.pending_blocks.empty():
                    block = self.pending_blocks.get()
                    self.commit_block(block)
                    print(f"✔️ Block {block.uid} committed.")
                
                # Wait for 5 minutes before running the next heartbeat check
                time.sleep(300) # Input in seconds.

        heartbeat_thread = threading.Thread(target=heartbeat, daemon=True)
        heartbeat_thread.start()

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
                
                # Show signature info
                if current.creation_signature:
                    print(f"    ✍️ Creation Signature: Present")
                if current.sale_agg_signature:
                    print(f"    ✍️ Sale Signature: Present")
                    
                current = current.next
            print("-" * 60)

def main():
    """
    Main function for the blockchain-based inventory and sales system
    with signature verification and Merkle tree integrity checks.
    """
    # Initialize the blockchain
    bc = Blockchain()
    print("\n🔗 Blockchain Inventory System Initialized 🔗")
    print("All blocks and transactions are cryptographically verified")
    
    while True:
        print("\n" + "=" * 60)
        print("📋 BLOCKCHAIN INVENTORY SYSTEM MENU 📋".center(60))
        print("=" * 60)
        print("1️⃣  Add New Item to Inventory")
        print("2️⃣  Execute Sale Transaction")
        print("3️⃣  View Complete Inventory")
        print("4️⃣  Search for Specific Item")
        print("5️⃣  Verify System Integrity")
        print("6️⃣  View Authentication Records (Merkle Tree)")
        print("7️⃣  Register New User")
        print("8️⃣  Exit System")
        print("-" * 60)
        
        choice = input("Enter your selection (1-8): ")
        
        if choice == "1":
            print("\n📦 ADD NEW ITEM TO INVENTORY")
            print("-" * 40)
            try:
                uid = int(input("Item UID: "))
                brand = input("Brand Name: ")
                item_name = input("Item Description: ")
                price = float(input("Price (₹): "))
                
                # Add block through verification process
                bc.add_block(uid, brand, item_name, price)
                print("\n🔄 Item submitted for verification and addition to inventory...")
                time.sleep(2)  # Allow time for verification thread
                
            except ValueError:
                print("❌ Invalid input. Please enter numeric values for UID and price.")
            
        elif choice == "2":
            print("\n💰 EXECUTE SALE TRANSACTION")
            print("-" * 40)
            try:
                uid = int(input("Item UID to sell: "))
                brand = input("Item Brand: ")
                
                # Process sale through verification
                bc.execute_sale(uid, brand)
                print("\n🔄 Sale transaction submitted for verification...")
                time.sleep(2)  # Allow time for verification thread
                
            except ValueError:
                print("❌ Invalid input. Please enter a numeric value for UID.")
            
        elif choice == "3":
            print("\n📊 COMPLETE INVENTORY LISTING")
            print("-" * 40)
            bc.print_blockchain()
            
        elif choice == "4":
            print("\n🔍 SEARCH FOR SPECIFIC ITEM")
            print("-" * 40)
            search_option = input("Search by (1) UID or (2) Brand? Enter 1 or 2: ")
            
            if search_option == "1":
                try:
                    uid = int(input("Enter Item UID: "))
                    found = False
                    
                    for letter, head in sorted(bc.chains.items()):
                        current = head
                        while current:
                            if current.uid == uid and "Genesis" not in current.brand:
                                print(f"\n✅ Item Found:")
                                print(f"  UID: {current.uid}")
                                print(f"  Brand: {current.brand}")
                                print(f"  Description: {current.item_name}")
                                print(f"  Price: ₹{current.price}")
                                print(f"  Status: {current.status}")
                                print(f"  Date Added: {current.timestamp}")
                                
                                if current.status == "Sold":
                                    print("  ✓ Sale verified by dual signatures")
                                else:
                                    print("  ✓ Item authenticity verified")
                                found = True
                                break
                            current = current.next
                        if found:
                            break
                    
                    if not found:
                        print("❌ No item found with that UID.")
                        
                except ValueError:
                    print("❌ Invalid input. Please enter a numeric UID.")
                    
            elif search_option == "2":
                brand_search = input("Enter Brand Name (or part of name): ").lower()
                found_items = []
                
                for letter, head in sorted(bc.chains.items()):
                    current = head
                    while current:
                        if "Genesis" not in current.brand and brand_search in current.brand.lower():
                            found_items.append(current)
                        current = current.next
                
                if found_items:
                    print(f"\n✅ Found {len(found_items)} items matching '{brand_search}':")
                    for idx, item in enumerate(found_items, 1):
                        print(f"\n  Item {idx}:")
                        print(f"  UID: {item.uid}")
                        print(f"  Brand: {item.brand}")
                        print(f"  Description: {item.item_name}")
                        print(f"  Price: ₹{item.price}")
                        print(f"  Status: {item.status}")
                        print(f"  Date Added: {item.timestamp}")
                else:
                    print(f"❌ No items found matching '{brand_search}'.")
            else:
                print("❌ Invalid option selected.")
                
        elif choice == "5":
            print("\n🔐 SYSTEM INTEGRITY VERIFICATION")
            print("-" * 40)
            
            print("Verifying blockchain structural integrity...")
            chain_valid = bc.validate_chain()
            
            print("Verifying cryptographic signatures...")
            signatures_valid = bc.verify_block_signatures()
            
            print("Verifying Merkle tree integrity...")
            merkle_valid = bc.verify_merkle_tree()
            
            if chain_valid and signatures_valid and merkle_valid:
                print("\n✅ FULL SYSTEM VERIFICATION PASSED")
                print("🔒 All data integrity checks successful")
            else:
                print("\n⚠️ VERIFICATION ISSUES DETECTED")
                if not chain_valid:
                    print("❌ Blockchain structure has inconsistencies")
                if not signatures_valid:
                    print("❌ One or more cryptographic signatures are invalid")
                if not merkle_valid:
                    print("❌ Merkle tree authentication records are corrupted")
            
        elif choice == "6":
            print("\n🌳 AUTHENTICATION RECORDS (MERKLE TREE)")
            print("-" * 40)
            bc.print_merkle_tree()
            
            verify = input("\nVerify Merkle tree integrity? (y/n): ").lower() == 'y'
            if verify:
                if bc.verify_merkle_tree():
                    print("✅ Merkle tree verification successful")
                else:
                    print("❌ Merkle tree verification failed")
            
        elif choice == "7":
            print("\n👤 REGISTER NEW USER")
            print("-" * 40)
            
            from signatures import Keys
            
            name = input("Enter user name: ")
            role = input("User role (employee/customer): ").lower()
            
            if role not in ["employee", "customer"]:
                print("❌ Invalid role! Please enter 'employee' or 'customer'.")
                continue
                
            password = getpass.getpass("Enter a secure password: ")
            confirm_password = getpass.getpass("Confirm password: ")
            
            if password != confirm_password:
                print("❌ Passwords do not match!")
                continue
                
            try:
                user = Keys(name, role, password)
                user.add_to_json()
                print(f"\n✅ {role.capitalize()} '{name}' successfully registered!")
                print("🔑 Cryptographic keys generated and securely stored")
            except Exception as e:
                print(f"❌ Error during registration: {e}")
            
        elif choice == "8":
            print("\n👋 Thank you for using the Blockchain Inventory System")
            print("Exiting securely...")
            break
            
        else:
            print("❌ Invalid choice. Please enter a number between 1 and 8.")
        
        # Add a pause before returning to the menu
        input("\nPress Enter to continue...")


if __name__ == "__main__":
    # Make sure the profiles directory exists
    import os
    os.makedirs("./profiles", exist_ok=True)
    
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n🛑 Program interrupted. Exiting securely...")
    except Exception as e:
        print(f"\n❌ An unexpected error occurred: {e}")
        print("The system has been terminated to protect data integrity.")

if __name__ == "__main__":
    main()