from blspy import PrivateKey, BasicSchemeMPL, G1Element
import os
import json

# BLS Group Order (r)
GROUP_ORDER = 0x73eda753299d7d483339d80809a1d80553bda402fffe5bfeffffffff00000001

# Generate a valid private/public key pair
def generate_key_pair():
    while True:
        sk_int = int.from_bytes(os.urandom(32), "big") % GROUP_ORDER
        if sk_int != 0:  # Ensure it's not zero
            break
    sk = PrivateKey.from_bytes(sk_int.to_bytes(32, "big"))
    pk = sk.get_g1()
    return sk, pk

# Initialize employees and customers
num_employees = 3
num_customers = 3

employees = [generate_key_pair() for _ in range(num_employees)]
customers = [generate_key_pair() for _ in range(num_customers)]

# Extract secret and public keys
employee_sks, employee_pks = zip(*employees)
customer_sks, customer_pks = zip(*customers)

# Function to sign data
def sign_data(sk, data):
    message = json.dumps(data, sort_keys=True).encode("utf-8")
    return BasicSchemeMPL.sign(sk, message)

# Function for sale transaction signing (with aggregated signatures)
def process_sale(employee_sk, customer_sk, data):
    message = json.dumps(data, sort_keys=True).encode("utf-8")
    
    # Generate individual signatures
    employee_signature = BasicSchemeMPL.sign(employee_sk, message)
    customer_signature = BasicSchemeMPL.sign(customer_sk, message)

    # Aggregate signatures
    try:
        aggregated_signature = BasicSchemeMPL.aggregate([
            employee_signature, 
            customer_signature
        ])
        return aggregated_signature, message
    except Exception as e:
        print(f"Signature aggregation error: {e}")
        return None, message

# Function to verify the sale transaction using only the master public key
def verify_sale(master_pk, aggregated_signature, message):
    try:
        return BasicSchemeMPL.verify(master_pk, message, aggregated_signature)
    except Exception as e:
        print(f"Verification error: {e}")
        return False

# --- SALE TRANSACTION ---
sale_data = {"product_id": 101, "status": "pending", "price": 5000}

# Select an employee and a customer
employee_sk, employee_pk = employee_sks[0], employee_pks[0]
customer_sk, customer_pk = customer_sks[0], customer_pks[0]

# Compute the "master" public key as the sum of employee and customer keys
master_public_key = employee_pk + customer_pk  # Key aggregation

# Employee & Customer sign the sale transaction
sale_signature, message = process_sale(employee_sk, customer_sk, sale_data)

# Verify if signature was successfully created
if sale_signature is not None:
    # Verify using only the master public key
    if verify_sale(master_public_key, sale_signature, message):
        sale_data["status"] = "sold"
        print("✅ Sale verified by Auditor and status updated to SOLD")
    else:
        print("❌ Sale verification failed")
else:
    print("❌ Failed to create signature")

print("🔹 Final Sale Data:", sale_data)
