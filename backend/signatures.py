import json
import getpass
import base64
import os
import bcrypt
import hashlib
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from blspy import PrivateKey, G2Element, G1Element, PublicKeyMPL as PublicKey, AugSchemeMPL
from collections import deque

BLS_GROUP_ORDER = 0x73eda753299d7d483339d80809a1d80553bda402fffe5bfeffffffff00000001

class Keys:
    def __init__(self, name, role, password):
        self.name = name
        self.role = role
        self.salt = bcrypt.gensalt()  # Generate bcrypt salt
        self.nonce = os.urandom(12)  # Generate a random nonce for AES-GCM
        self.hashed_password = self.hash_password(password)  # Hash password using bcrypt
        self.encryption_key = self.derive_key(password)  # Derive encryption key using PBKDF2
        self.private_key, self.public_key = self.generate_bls_keys(password)  # Generate BLS keys
        self.encrypted_private_key = self.encrypt_private_key()  # Encrypt private key

    def hash_password(self, password):
        """Hashes a password using bcrypt."""
        return bcrypt.hashpw(password.encode(), self.salt).decode()

    def derive_key(self, password):
        """Derives an AES encryption key from a password using PBKDF2."""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
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
        filename = f"./profiles/{self.role}s.json"
        data_entry = {
            "name": self.name,
            "hashed_password": self.hashed_password,
            "public_key": base64.b64encode(self.public_key).decode(),
            "encrypted_private_key": self.encrypted_private_key,  # Already a Base64 string
            "salt": self.salt.decode(),  # Store bcrypt salt as string
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
        filename = f"./profiles/{role}s.json"
        try:
            with open(filename, "r") as file:
                users = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            print("No registered users found.")
            return None
        for user in users:
            if user["name"] == name:
                stored_hashed_password = user["hashed_password"].encode()
                salt = user["salt"].encode()
                encrypted_data = base64.b64decode(user["encrypted_private_key"])
                nonce, tag, ciphertext = encrypted_data[:12], encrypted_data[12:28], encrypted_data[28:]
                
                # Verify password
                if bcrypt.checkpw(input_password.encode(), stored_hashed_password):
                    print("\n✅ Password correct! Now verifying 2FA...")
                    otp = input("Enter the 6-digit 2FA code: ")
                    if otp != "123456":
                        print("❌ 2FA verification failed!")
                        return None
                    encryption_key = Keys.derive_key_static(input_password, salt)
                    cipher = Cipher(algorithms.AES(encryption_key), modes.GCM(nonce, tag))
                    decryptor = cipher.decryptor()
                    private_key = decryptor.update(ciphertext) + decryptor.finalize()
                    public_key = base64.b64decode(user["public_key"]) 
                    print("\n🔓 Private Key Successfully Retrieved!")
                    return private_key.hex(), public_key
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

class Signing:
    @staticmethod
    def sign_data(name, role, password, data):
        priv_key_hex, public_key = Keys.authenticate_and_decrypt(name, role, password)
        if priv_key_hex is None:
            print("❌ Authentication failed. Unable to sign data.")
            return None
        else:
            private_key = PrivateKey.from_bytes(bytes.fromhex(priv_key_hex))
            message = data.encode()
            signature = AugSchemeMPL.sign(private_key, message)
            
            # Convert public key to base64 before adding to Merkle tree
            public_key_b64 = base64.b64encode(public_key).decode()
            
            return base64.b64encode(bytes(signature)).decode(), public_key_b64
    
    @staticmethod
    def sign_data_dual(emp_name, emp_password, cust_name, cust_password, data):
        emp_private_key_hex, emp_public_key = Keys.authenticate_and_decrypt(emp_name, "employee", emp_password)
        cust_private_key_hex, cust_public_key = Keys.authenticate_and_decrypt(cust_name, "customer", cust_password)

        if not emp_private_key_hex or not cust_private_key_hex:
            print("❌ Authentication failed for one or both users. Unable to sign data.")
            return None
        
        message = data.encode()
        
        # Create proper private key objects
        emp_private_key = PrivateKey.from_bytes(bytes.fromhex(emp_private_key_hex))
        cust_private_key = PrivateKey.from_bytes(bytes.fromhex(cust_private_key_hex))
        
        # Get public keys from private keys to ensure consistency
        emp_pub = emp_private_key.get_g1()
        cust_pub = cust_private_key.get_g1()
        
        # Sign the message with each key using AugSchemeMPL
        emp_signature = AugSchemeMPL.sign(emp_private_key, message)
        cust_signature = AugSchemeMPL.sign(cust_private_key, message)
        
        # Aggregate signatures in the correct order
        signatures = [emp_signature, cust_signature]
        aggregated_signature = AugSchemeMPL.aggregate(signatures)
        
        # Store the PUBLIC KEYS in the correct order for verification
        pub_keys = [emp_pub, cust_pub]
        
        # Pack both public keys into a special format for the verifier
        # This is critical - we need to store the individual keys, not just their sum
        packed_pub_keys = json.dumps([
            base64.b64encode(bytes(emp_pub)).decode(),
            base64.b64encode(bytes(cust_pub)).decode()
        ])
        
        return (
            base64.b64encode(bytes(aggregated_signature)).decode(), 
            packed_pub_keys  # This is now a JSON string containing both public keys
        )
    
    @staticmethod
    def verify_signature(public_key_data, data, signature_b64):
        """Verifies if the given signature is valid for the provided data and public key."""
        message = data.encode()
        signature = G2Element.from_bytes(base64.b64decode(signature_b64))
        
        # Check if this is a single key or a JSON-packed array of keys
        try:
            # Try to parse as JSON - this would be the case for dual signatures
            pub_key_array = json.loads(public_key_data)
            if isinstance(pub_key_array, list) and len(pub_key_array) > 1:
                # This is an aggregated signature case
                print("Detected multi-signature format...")
                pub_keys = [G1Element.from_bytes(base64.b64decode(pk)) for pk in pub_key_array]
                result = AugSchemeMPL.aggregate_verify(pub_keys, [message] * len(pub_keys), signature)
                return result
        except (json.JSONDecodeError, TypeError):
            # Not JSON, so treat as a single key
            pass
            
        # Handle regular single signature case
        try:
            public_key = PublicKey.from_bytes(base64.b64decode(public_key_data))
            return AugSchemeMPL.verify(public_key, message, signature)
        except Exception as e:
            print(f"Single signature verification error: {str(e)}")
            try:
                public_key = G1Element.from_bytes(base64.b64decode(public_key_data))
                return AugSchemeMPL.verify(public_key, message, signature)
            except Exception as e:
                print(f"G1Element verification error: {str(e)}")
                return False
class MerkleNode:
    def __init__(self, value):
        self.data = value
        self.left = None
        self.right = None
        self.parent = None

class MerkleTree:
    def __init__(self):
        self.public_keys = []  # List of Tuples, each a leaf node
        self.root = None

    def add_block_keys(self, creation_pubkey_b64, sale_pubkey_b64=None):
        """ 
        Adds new public key pair to the tree or updates an existing entry.
        If creation_pubkey_b64 already exists with a None sale key, 
        and sale_pubkey_b64 is provided, update the existing tuple.
        """
        # First, check if creation_pubkey_b64 already exists with None sale key
        for i, (existing_creation_key, existing_sale_key) in enumerate(self.public_keys):
            if existing_creation_key == creation_pubkey_b64 and existing_sale_key == "":
                # If sale_pubkey_b64 is provided, update the existing tuple
                if sale_pubkey_b64 is not None:
                    self.public_keys[i] = (existing_creation_key, sale_pubkey_b64)
                    self._build_merkle_tree()
                return

        # If no existing entry found or no update made, append new tuple
        self.public_keys.append((creation_pubkey_b64, sale_pubkey_b64 or ""))
        self._build_merkle_tree()

    def _build_merkle_tree(self):
        """ Constructs a Merkle Tree from the stored keys. """
        if not self.public_keys:
            return

        # Step 1: Create leaf nodes
        nodes = []
        for creation_key, sale_key in self.public_keys:
            node0 = MerkleNode(creation_key)  
            node1 = MerkleNode(sale_key)
            parent_hash = hashlib.sha256((creation_key + sale_key).encode()).hexdigest()
            parent = MerkleNode(parent_hash)
            parent.left = node0
            parent.right = node1
            node0.parent = parent
            node1.parent = parent
            nodes.append(parent)

        # Step 2: Build tree upwards until root is reached
        while len(nodes) > 1:
            new_level = []
            if len(nodes) % 2 != 0:
                nodes.append(nodes[-1])  # Duplicate last node if odd number
            
            for i in range(0, len(nodes), 2):
                combined_hash = hashlib.sha256((nodes[i].data + nodes[i+1].data).encode()).hexdigest()
                parent = MerkleNode(combined_hash)
                parent.left = nodes[i]
                parent.right = nodes[i+1]
                nodes[i].parent = parent
                nodes[i+1].parent = parent
                new_level.append(parent)

            nodes = new_level  # Move to the next level

        self.root = nodes[0]  # Final root node

    def verify_merkle(self):
        """ Verifies the Merkle Tree by recomputing hashes from leaf to root. """
        if not self.root or not self.public_keys:
            return False  # No tree to verify
        
        # Step 1: Reconstruct leaf nodes
        nodes = []
        for creation_key, sale_key in self.public_keys:
            node0_hash = hashlib.sha256(creation_key.encode()).hexdigest()
            node1_hash = hashlib.sha256(sale_key.encode()).hexdigest()
            parent_hash = hashlib.sha256((creation_key + sale_key).encode()).hexdigest()
            nodes.append(parent_hash)
        
        # Step 2: Rebuild the tree upwards
        while len(nodes) > 1:
            new_level = []
            if len(nodes) % 2 != 0:
                nodes.append(nodes[-1])  # Duplicate last node if odd number
            
            for i in range(0, len(nodes), 2):
                combined_hash = hashlib.sha256((nodes[i] + nodes[i+1]).encode()).hexdigest()
                new_level.append(combined_hash)
            
            nodes = new_level  # Move up a level
        
        # Step 3: Compare the computed root with stored root
        return nodes[0] == self.root.data




def print_merkle_tree(root):
    """Prints the Merkle tree in a level-wise format."""
    if not root:
        print("The Merkle tree is empty.")
        return

    queue = deque([(root, 0)])  # (node, level)
    current_level = 0
    result = []

    while queue:
        node, level = queue.popleft()

        # Move to a new level in the output
        if level > current_level:
            print(" | ".join(result))  # Print current level
            result = []  # Reset list for new level
            current_level = level

        # Add node data (shorten hash for readability)
        result.append(node.data[:8] + "..." if len(node.data) > 8 else node.data)

        # Add children to the queue
        if node.left:
            queue.append((node.left, level + 1))
        if node.right:
            queue.append((node.right, level + 1))

    # Print last level
    if result:
        print(" | ".join(result))

def print_merkle_tree_recursive(node, level=0):
    """Prints the Merkle tree in an indented hierarchical format."""
    if node is None:
        return
    
    print(" " * (4 * level) + "|-- " + (node.data[:8] + "..." if len(node.data) > 8 else node.data))
    
    # Print left and right children
    if node.left or node.right:  # Only print children if they exist
        print_merkle_tree_recursive(node.left, level + 1)
        print_merkle_tree_recursive(node.right, level + 1)

# ================================
# 🌟 Menu-Based `main()` Function
# ================================
def main():
    import os
    
    # Create profiles directory if it doesn't exist
    if not os.path.exists('./profiles'):
        os.makedirs('./profiles')
    
    while True:
        print("\n🔐 BLS Signature Testing System")
        print("=" * 40)
        print("1️⃣ Register New User (Employee/Customer)")
        print("2️⃣ Test Single Signature")
        print("3️⃣ Test Dual Signature")
        print("4️⃣ Verify a Signature")
        print("5️⃣ Merkle Tree Operations")
        print("6️⃣ Exit")
        choice = input("\nEnter your choice: ")

        if choice == "1":
            # Register a new user
            name = input("Enter username: ")
            role = input("Role (employee/customer): ").lower()
            
            if role not in ["employee", "customer"]:
                print("❌ Invalid role! Please enter 'employee' or 'customer'.")
                continue
                
            password = getpass.getpass("Enter a secure password: ")
            user = Keys(name, role, password)
            user.add_to_json()
            
            print(f"\n✅ {role.capitalize()} '{name}' successfully registered!")

        elif choice == "2":
            # Test single signature
            name = input("Enter username: ")
            role = input("Role (employee/customer): ").lower()
            
            if role not in ["employee", "customer"]:
                print("❌ Invalid role! Please enter 'employee' or 'customer'.")
                continue
                
            password = getpass.getpass("Enter password: ")
            data = input("Enter data to sign: ")
            
            print("\n🔑 Signing data...")
            signature_result = Signing.sign_data(name, role, password, data)
            
            if signature_result:
                signature, public_key = signature_result
                print("\n✅ Signature created successfully!")
                print(f"Signature: {signature[:20]}...")
                print(f"Public Key: {public_key[:20]}...")
                
                # Verify immediately
                if Signing.verify_signature(public_key, data, signature):
                    print("✅ Signature verified successfully!")
                else:
                    print("❌ Signature verification failed!")
            else:
                print("❌ Failed to create signature.")

        elif choice == "3":
            # Test dual signature
            print("\n🔄 Dual Signature Test (Employee + Customer)")
            emp_name = input("Enter employee name: ")
            emp_password = getpass.getpass("Enter employee password: ")
            
            cust_name = input("Enter customer name: ")
            cust_password = getpass.getpass("Enter customer password: ")
            
            data = input("Enter data to sign: ")
            
            print("\n🔑 Creating dual signature...")
            dual_result = Signing.sign_data_dual(emp_name, emp_password, cust_name, cust_password, data)
            
            if dual_result:
                agg_signature, agg_pubkey = dual_result
                print("\n✅ Dual signature created successfully!")
                print(f"Aggregated Signature: {agg_signature[:20]}...")
                print(f"Aggregated Public Key: {agg_pubkey[:20]}...")
                
                # Verify immediately
                print("\n🔍 Verifying dual signature...")
                if Signing.verify_signature(agg_pubkey, data, agg_signature):
                    print("✅ Dual signature verified successfully!")
                else:
                    print("❌ Dual signature verification failed!")
                    print("\nDebugging information:")
                    print(f"Data being verified: '{data}'")
                    try:
                        # For debugging - try both verification approaches
                        signature = G2Element.from_bytes(base64.b64decode(agg_signature))
                        pubkey1 = PublicKey.from_bytes(base64.b64decode(agg_pubkey))
                        result1 = AugSchemeMPL.verify(pubkey1, data.encode(), signature)
                        print(f"Verify using PublicKey: {result1}")
                    except Exception as e:
                        print(f"PublicKey verification error: {str(e)}")
                    
                    try:
                        signature = G2Element.from_bytes(base64.b64decode(agg_signature))
                        pubkey2 = G1Element.from_bytes(base64.b64decode(agg_pubkey))
                        result2 = AugSchemeMPL.verify(pubkey2, data.encode(), signature)
                        print(f"Verify using G1Element: {result2}")
                    except Exception as e:
                        print(f"G1Element verification error: {str(e)}")
            else:
                print("❌ Failed to create dual signature.")

        elif choice == "4":
            # Verify an existing signature
            public_key_b64 = input("Enter public key (base64): ")
            signature_b64 = input("Enter signature (base64): ")
            data = input("Enter the original data: ")
            
            print("\n🔍 Verifying signature...")
            if Signing.verify_signature(public_key_b64, data, signature_b64):
                print("✅ Signature verified successfully!")
            else:
                print("❌ Signature verification failed!")

        elif choice == "5":
            # Merkle Tree operations
            print("\n🌲 Merkle Tree Operations")
            print("1. Create/Update Merkle Tree")
            print("2. Print Merkle Tree")
            print("3. Verify Merkle Tree")
            print("4. Back to Main Menu")
            tree_choice = input("\nEnter your choice: ")
            
            if tree_choice == "1":
                tree = MerkleTree()
                num_entries = int(input("How many key pairs to add? "))
                
                for i in range(num_entries):
                    creation_key = input(f"Entry {i+1} - Creation Public Key: ")
                    sale_key = input(f"Entry {i+1} - Sale Public Key (leave empty if none): ")
                    tree.add_block_keys(creation_key, sale_key if sale_key else None)
                
                print("✅ Merkle Tree created/updated successfully!")
                
            elif tree_choice == "2":
                tree = MerkleTree()
                # For demo purposes, add some sample data
                tree.add_block_keys("Sample_Creation_Key_1", "Sample_Sale_Key_1")
                tree.add_block_keys("Sample_Creation_Key_2", "Sample_Sale_Key_2")
                
                print("\nHierarchical View:")
                print_merkle_tree_recursive(tree.root)
                
                print("\nLevel-wise View:")
                print_merkle_tree(tree.root)
                
            elif tree_choice == "3":
                tree = MerkleTree()
                # For demo purposes, add some sample data
                tree.add_block_keys("Sample_Creation_Key_1", "Sample_Sale_Key_1")
                tree.add_block_keys("Sample_Creation_Key_2", "Sample_Sale_Key_2")
                
                if tree.verify_merkle():
                    print("✅ Merkle Tree verification successful!")
                else:
                    print("❌ Merkle Tree verification failed!")
            
            elif tree_choice == "4":
                continue
                
            else:
                print("❌ Invalid choice!")

        elif choice == "6":
            print("\n👋 Exiting BLS Signature Testing System. Goodbye!")
            break

        else:
            print("❌ Invalid choice! Please enter a number between 1 and 6.")


# Run the program
if __name__ == "__main__":
    main()
