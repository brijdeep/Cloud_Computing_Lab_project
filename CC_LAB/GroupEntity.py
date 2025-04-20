from UserEntity import UserEntity

class GroupEntity:
    def __init__(self, id, name, aclmap):
        self.id = id
        self.name = name
        self.aclmap = aclmap
        
    def add_user(self, user, user_key):
        self.aclmap[int(user.id)] = user_key

    def number_of_users(self):
        return len(self.aclmap)
    
    def remove_user(self, user):
        del self.aclmap[user.id]

    def user_exists(self, user):
        return user.id in self.aclmap
    
    def get_user_key(self, userId):
        return self.aclmap[userId]
    
    def set_user_key(self, userId, user_key):
        self.aclmap[userId] = user_key
    
    def __str__(self):
        return f"GroupEntity(id={self.id}, name={self.name}, aclmap={self.aclmap})"

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "aclmap": self.aclmap
        }

def create_group(self, id, name):
        return GroupEntity(id, name, {})