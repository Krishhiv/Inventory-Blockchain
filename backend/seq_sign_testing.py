import rsa

# Generate an RSA key pair
def generate_rsa_keys():
    public_key, private_key = rsa.newkeys(2048)
    return private_key, public_key

# Sign message with a given private key
def sign_message(private_key, message, key_owner):
    signature = rsa.sign(message, private_key, 'SHA-256')
    print(f"[SIGNING] {key_owner} signed the message. Signature (first 10 bytes): {signature[:10].hex()}...")
    return signature

# Verify a signature with a given public key
def verify_signature(public_key, message, signature, key_owner):
    try:
        rsa.verify(message, signature, public_key)
        print(f"[VERIFICATION] {key_owner}'s signature is VALID.")
        return True
    except rsa.VerificationError:
        print(f"[VERIFICATION] {key_owner}'s signature is INVALID!")
        return False

# Sequential Signing: First key signs, then second key signs (message + first signature)
def sequential_sign(private_key1, private_key2, message):
    print("\n=== SEQUENTIAL SIGNING PROCESS STARTED ===")
    sig1 = rsa.sign(message, private_key1, 'SHA-256')
    combined_message = message + sig1  # Combine message with first signature
    sig2 = rsa.sign(combined_message, private_key2, 'SHA-256')
    print("=== SEQUENTIAL SIGNING COMPLETED ===\n")
    return sig2, sig1  # Return both signatures

# Sequential Verification: Ensures both keys were used
def sequential_verify(public_key1, public_key2, message, sig2, sig1):
    print("\n=== SEQUENTIAL VERIFICATION PROCESS STARTED ===")
    combined_message = message + sig1  # Recreate combined message

    # Verify second signature first
    is_valid2 = verify_signature(public_key2, combined_message, sig2, "Key 2 (Second)")
    
    # Verify first signature
    is_valid1 = verify_signature(public_key1, message, sig1, "Key 1 (First)")

    if is_valid1 and is_valid2:
        print("[FINAL VERIFICATION] Message successfully verified by both signatures!")
    else:
        print("[FINAL VERIFICATION] Message verification FAILED!")

    print("=== SEQUENTIAL VERIFICATION COMPLETED ===\n")
    return is_valid1 and is_valid2

# Main Execution
message = b"Hello, this is a test message."

# Generate two sets of RSA keys
private_key1, public_key1 = generate_rsa_keys()
private_key2, public_key2 = generate_rsa_keys()

# Perform sequential signing
sig2, sig1 = sequential_sign(private_key1, private_key2, message)

# Verify both signatures
is_valid = sequential_verify(public_key1, public_key2, message, sig2, sig1)

# Output final result
print(f"\nFinal Verification Result: {'SUCCESS' if is_valid else 'FAILED'}")
