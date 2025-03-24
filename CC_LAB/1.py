from pymongo import MongoClient

# MongoDB Atlas connection string
CONNECTION_STRING = "mongodb+srv://112215212:1YsvpxvtfQF9QGBP@cluster0.kfsii.mongodb.net/?retryWrites=true&w=majority&appName=cluster0"

# Connect to MongoDB Atlas
client = MongoClient(CONNECTION_STRING)

# Access the database and collection
db = client["sedasc_db"]
acl_collection = db["access_control_list"]

# Insert a sample document
sample_data = {
    "file_id": "file123",
    "user_id": "user1",
    "key_part": "K1"
}
acl_collection.insert_one(sample_data)
print("Document inserted successfully!")

# Query the database
result = acl_collection.find_one({"file_id": "file123"})
print("Retrieved Document:", result)
