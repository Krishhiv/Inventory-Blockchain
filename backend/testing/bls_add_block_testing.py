from blspy import PrivateKey, AugSchemeMPL, G1Element
import json

def generate_key_pair():
    sk = PrivateKey.from_bytes(bytes(range(32)))  # Generate a random private key
    pk = sk.get_g1()
    return sk, pk

# Simulate multiple employees and customers
num_employees = 3
num_customers = 3

employees = [generate_key_pair() for _ in range(num_employees)]
customers = [generate_key_pair() for _ in range(num_customers)]

# Extract public keys for aggregation
employee_pks = [pk for _, pk in employees]
customer_pks = [pk for _, pk in customers]

# Auditor's master public key (aggregated public key of all employees and customers)
auditor_master_pk = sum(employee_pks + customer_pks, G1Element())

# Example: Employee signing data
def sign_data(sk, data):
    message = json.dumps(data, sort_keys=True).encode("utf-8")
    signature = AugSchemeMPL.sign(sk, message)
    return signature

def verify_signature(pk, signature, data):
    message = json.dumps(data, sort_keys=True).encode("utf-8")
    return AugSchemeMPL.verify(pk, message, signature)

# Employee 1 signs data
print("Employee 1 is signing the data.")
sample_data = {"product_id": 101, "status": "sold", "price": 5000}
employee_sk, employee_pk = employees[0]
employee_signature = sign_data(employee_sk, sample_data)

# Auditor verifies the signature
is_valid = verify_signature(employee_pk, employee_signature, sample_data)
print("Signature valid?", is_valid)

sample_data_2 = {"product_id": 101, "status": "sold", "price": 5000}
