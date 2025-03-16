from cryptography.hazmat.primitives.asymmetric import rsa, padding # type: ignore
from cryptography.hazmat.primitives import hashes, serialization # type: ignore
import base64
import os

# ✅ Generate RSA key for the company (called once during setup)
def generate_company_keys():
    """Generates an RSA key pair for the company if not already created."""
    if not os.path.exists("private_key.pem") or not os.path.exists("public_key.pem"):
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        public_key = private_key.public_key()

        # Save the company's private key securely
        with open("private_key.pem", "wb") as private_file:
            private_file.write(
                private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption(),
                )
            )

        # Save the company's public key
        with open("public_key.pem", "wb") as public_file:
            public_file.write(
                public_key.public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo,
                )
            )

        print("✅ Company keys generated: private_key.pem & public_key.pem")
    else:
        print("🔹 Company keys already exist.")


# ✅ Generate a new RSA key for the customer (done at the time of sale)
def generate_keys_for_customer(customer_name):
    """Generates an RSA key pair for the customer at the time of sale."""
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )
    public_key = private_key.public_key()

    # Save the customer's private key securely
    with open(f"{customer_name}_private.pem", "wb") as private_file:
        private_file.write(
            private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption(),
            )
        )

    # Save the customer's public key
    with open(f"{customer_name}_public.pem", "wb") as public_file:
        public_file.write(
            public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo,
            )
        )

    print(f"✅ Keys generated for {customer_name}: {customer_name}_private.pem & {customer_name}_public.pem")


# ✅ Sign the sale transaction (used by both company & customer)
def sign_transaction(data, private_key_path):
    """Signs transaction data using the given private key."""
    with open(private_key_path, "rb") as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=None
        )

    # Sign the transaction data
    signature = private_key.sign(
        data.encode(),
        padding.PKCS1v15(),
        hashes.SHA256()
    )

    # Return the signature in base64 format
    return base64.b64encode(signature).decode()


# ✅ Verify that both company & customer signed the transaction
def verify_transaction(data, signatures, public_keys):
    """Verifies a transaction by checking both company & customer signatures."""
    for i in range(2):  # We expect exactly two signatures (company & customer)
        with open(public_keys[i], "rb") as key_file:
            public_key = serialization.load_pem_public_key(
                key_file.read()
            )

        try:
            # Decode the signature
            signature = base64.b64decode(signatures[i])

            # Verify the signature
            public_key.verify(
                signature,
                data.encode(),
                padding.PKCS1v15(),
                hashes.SHA256()
            )
        except Exception:
            return False  # Signature invalid

    return True  # Both signatures are valid
