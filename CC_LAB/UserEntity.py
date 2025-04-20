from config import MONGO_URI
from pymongo import MongoClient

client = MongoClient(MONGO_URI)
db = client["sedasc_db"]
user_collection = db["user_part"]

class UserEntity:
    def __init__(self, id, name):
        self.id = id
        self.name = name

    def __str__(self):
        return f"UserEntity(id={self.id}, name={self.name})"
    
    def id(self):
        return self.id
    
    def name(self):
        return self.name
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name
        }
    
    
    # def store_user(self, id, name):
    #     user_data = {
    #         "user_id": id,
    #         "user_name": name
    #     }
    #     user_collection.insert_one(user_data)
    #     print("✅ User stored in MongoDB Atlas!")

    # def get_user(self, id):
    #     user = user_collection.find_one({"user_id": id})
    #     return user
    
    # def user_exists(self, id):
    #     user = user_collection.find_one({"user_id": id})
    #     return user is not None
    
    # def delete_user(self, id):
    #     user_collection.delete_one({"user_id": id})
    #     print("✅ User deleted from MongoDB Atlas!")    

    # def update_user(self, id, name):
    #     user_collection.update_one({"user_id": id}, {"$set": {"user_name": name}})

    # def get_all_users(self):    
    #     users = user_collection.find()
    #     return users
    
    
        

    