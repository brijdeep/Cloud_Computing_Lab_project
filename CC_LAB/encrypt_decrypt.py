from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os

# Encrypt the file using AES key
def encrypt_file(input_file, output_file, key):
    iv = os.urandom(16)

    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
    encryptor = cipher.encryptor()

    with open(input_file, 'rb') as f:
        plaintext = f.read()

    ciphertext = encryptor.update(plaintext) + encryptor.finalize()

    with open(output_file, 'wb') as f:
        f.write(iv + ciphertext)

    print(f"✅ Encrypted file saved to: {output_file}")


def decrypt_file(input_file, output_file, key):

    with open(input_file, 'rb') as f:
        data = f.read()

    # Extract IV and ciphertext
    iv = data[:16]
    ciphertext = data[16:]

    # Initialize cipher for decryption
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
    decryptor = cipher.decryptor()

    # Decrypt the ciphertext
    plaintext = decryptor.update(ciphertext) + decryptor.finalize()

    # Write the decrypted content to the output file
    with open(output_file, 'wb') as f:
        f.write(plaintext)

    print(f"✅ Decrypted file saved to: {output_file}")

# Example usage
if __name__ == "__main__":
    # For demonstration: use a random 32-byte key
    aes_key = os.urandom(32)

    input_file = "test.txt"
    encrypted_file = "encrypted_file.enc"
    decrypted_file = "decrypted_file.txt"

    # Encrypt the file
    encrypt_file(input_file, encrypted_file, aes_key)

    # Decrypt the file
    decrypt_file(encrypted_file, decrypted_file, aes_key)
