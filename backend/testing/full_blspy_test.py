from blspy import PrivateKey

private_key_bytes = bytes.fromhex("51ceb6392cbfe0adbb6a8207aee03a01b38488be5ff1266968a7f5f8aaa5dcdd")
private_key = PrivateKey.from_bytes(private_key_bytes)

print("✅ Private Key is valid!")
print("Public Key:", private_key.get_g1())
