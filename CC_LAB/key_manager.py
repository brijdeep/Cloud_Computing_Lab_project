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

def generate_keyid(groupid, userid):
    key_bytes = f"{userid}:{groupid}".encode()
    return base64.urlsafe_b64encode(key_bytes).decode()

# Generate AES Key
def generate_aes_key():
    key = os.urandom(32)  # 256-bit key
    print("✅ Generated AES Key:", base64.b64encode(key).decode())
    return key


def split_key(key):
    part1 = os.urandom(32)
    part2 = bytes(a ^ b for a,b in zip(part1, key))
    print("🔑 Part 1 (CS):", base64.b64encode(part1).decode())
    print("🔑 Part 2 (User):", base64.b64encode(part2).decode())
    return part1, part2

def join_key(part1, part2):
    return bytes(a ^ b for a,b in zip(part1, part2))

# Store Part 1 in MongoDB Atlas
def store_key(part1, groupid, userid):
    key_part1_encoded = base64.b64encode(part1).decode()
    key_data = {
        "key_id": generate_keyid(groupid, userid),
        "part1": key_part1_encoded
    }
    key_collection.insert_one(key_data)
    print("✅ Key Part 1 stored in MongoDB Atlas!")

def get_key(groupid, userid):
    key_data = key_collection.find_one({"key_id": generate_keyid(groupid, userid)})
    if key_data is None:
        return None
    key_part1_encoded = key_data["part1"]
    return key_part1_encoded  


# Main Execution
if __name__ == "__main__":
    print("🔐 Generating AES Key...")
    # aes_key = generate_aes_key()
    # part1, part2 = split_key(aes_key)
    
    # # Store Part 1 in MongoDB Atlas
    # store_key(part1)
    # print("🔐 Part 2 (send to user):", base64.b64encode(part2).decode())
    # print("getting key: ", get_key(54, 54))
    # print("Original key: ", base64.b64encode(join_key(part1, part2)).decode())
