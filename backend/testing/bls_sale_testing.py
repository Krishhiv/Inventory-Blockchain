from blspy import PrivateKey, AugSchemeMPL, G1Element
import json
import os

# Generate private and public keys for an employee
def generate_key_pair():
    sk = PrivateKey.from_seed(os.urandom(32))  # Ensure 32 bytes for a valid private key
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

print("Employee Public Keys:", employee_pks)
print("Customer Public Keys:", customer_pks)
print("Auditor Master Public Key:", auditor_master_pk)
print()
print("---------------------------------")
print("---------------------------------")
print()

# Signing data
def sign_data(sk, data):
    message = json.dumps(data, sort_keys=True).encode("utf-8")
    signature = AugSchemeMPL.sign(sk, message)
    return signature

# Verifying the signature
def verify_signature(pk, signature, data):
    message = json.dumps(data, sort_keys=True).encode("utf-8")
    return AugSchemeMPL.verify(pk, message, signature)

# Sale transaction: Employee and customer sign the transaction
def process_sale(employee_sk, customer_sk, data):
    employee_signature = sign_data(employee_sk, data)
    customer_signature = sign_data(customer_sk, data)
    
    # Aggregate the two signatures
    aggregated_signature = AugSchemeMPL.aggregate([employee_signature, customer_signature])
    return aggregated_signature

# Auditor verifies the sale transaction using the master public key
def verify_sale(auditor_pk, aggregated_signature, data):
    message = json.dumps(data, sort_keys=True).encode("utf-8")
    return AugSchemeMPL.verify(auditor_pk, message, aggregated_signature)


# Sample sale transaction
sale_data = {"product_id": 102, "status": "available", "price": 7500}

# Select an employee and a customer
employee_sk, employee_pk = employees[1]
customer_sk, customer_pk = customers[1]

# Both sign the transaction
sale_signature = process_sale(employee_sk, customer_sk, sale_data)

# Auditor verifies the transaction
if verify_sale(auditor_master_pk, sale_signature, sale_data):
    sale_data["status"] = "sold"
    print("Sale Number 1 verified and status updated to SOLD")
else:
    print("Sale verification failed")

print("Final Sale Data:", sale_data)

# SALE 2 AFTER ADDING NEW EMPLOYEES AND CUSTOMERS

""" new_employees = [generate_key_pair() for _ in range(3)]
new_customers = [generate_key_pair() for _ in range(3)]

employees.append(new_employees)
customers.append(new_customers)

employee_pks = [pk for _, pk in employees]
customer_pks = [pk for _, pk in customers]

# Auditor's master public key (aggregated public key of all employees and customers)
auditor_master_pk = sum(employee_pks + customer_pks, G1Element())

new_sale_data = {"product_id": 313, "status": "available", "price": 25000}

employee_sk, employee_pk = employees[-1]
customer_sk, customer_pk = customers[4]

sale_signature = process_sale(employee_sk, customer_sk, new_sale_data) """
