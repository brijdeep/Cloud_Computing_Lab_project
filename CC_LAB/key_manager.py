from pymongo import MongoClient
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os
import base64
from config import MONGO_URI

# Connect to MongoDB Atlas
client = MongoClient(MONGO_URI)
db = client["sedasc_db"]
key_collection = db["key_part"]

# Generate AES Key
def generate_aes_key():
    key = os.urandom(32)  # 256-bit key
    print("✅ Generated AES Key:", base64.b64encode(key).decode())
    return key

# Split the Key
def split_key(key):
    # midpoint = len(key) // 2
    part1 = os.urandom(32)
    part2 = bytes(a ^ b for a,b in zip(part1, key))
    print("🔑 Part 1 (CS):", base64.b64encode(part1).decode())
    print("🔑 Part 2 (User):", base64.b64encode(part2).decode())
    return part1, part2

# Store Part 1 in MongoDB Atlas
def store_key(part1):
    key_part1_encoded = base64.b64encode(part1).decode()
    key_data = {
        "key_id": "key123",
        "part1": key_part1_encoded
    }
    key_collection.insert_one(key_data)
    print("✅ Key Part 1 stored in MongoDB Atlas!")

# Main Execution
if __name__ == "__main__":
    aes_key = generate_aes_key()
    part1, part2 = split_key(aes_key)
    
    # Store Part 1 in MongoDB Atlas
    store_key(part1)
    print("🔐 Part 2 (send to user):", base64.b64encode(part2).decode())
