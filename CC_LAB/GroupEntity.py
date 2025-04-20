from UserEntity import UserEntity
from enum import Enum

class Permission(Enum):
    READ = 1
    WRITE = 2
    EXECUTE = 3
    DELETE = 4


class GroupEntity:
    def __init__(self, id, name, keymap):
        self.id = id
        self.name = name
        self.keymap = keymap
        self.permap = {}
        
    def add_user(self, user, user_key, user_per = Permission.READ):
        if self.user_exists(user):
            print(f"❌ User {user.name} already exists in group {self.name}.")
            return
        self.keymap[int(user.id)] = user_key
        self.permap[int(user.id)] = user_per
        print(f"✅ User {user.name} added to group {self.name} with key {user_key} and permission {user_per}.")

    def number_of_users(self):
        return len(self.keymap)
    
    def remove_user(self, user):
        del self.keymap[user.id]

    def user_exists(self, user):
        return user.id in self.keymap
    
    def get_user_key(self, userId):
        return self.keymap[userId]
    
    def set_user_key(self, userId, user_key):
        self.keymap[userId] = user_key

    def get_user_permission(self, userId):
        return self.permap[userId]
    
    def set_user_permission(self, userId, user_per):
        self.permap[userId] = user_per
    
    def __str__(self):
        return f"GroupEntity(id={self.id}, name={self.name}, keymap={self.keymap})"

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "keymap": self.keymap
        }

def create_group(self, id, name):
        return GroupEntity(id, name, {})