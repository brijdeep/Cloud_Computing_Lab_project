from flask import Flask, request, jsonify
from key_manager import generate_aes_key, split_key, store_key, join_key, get_key
from encrypt_decrypt import encrypt_file, decrypt_file
import base64
import os
from UserEntity import UserEntity
from GroupEntity import GroupEntity, create_group

app = Flask(__name__)

userDict = {}
groupDict = {}

def fullkey(groupId, userId):
    #groupID and userID
    group = groupDict[groupId]
    part2 = group.get_user_key(userId)
    part1 = get_key(groupId, userId)

    return join_key(part1, part2)
   
#---------------------------------------------

@app.route('/api/user', methods=['GET'])
def get_user():
    try:
        userid = int(request.args.get('id'))
        print(userid)
        return jsonify(userDict[userid].to_dict()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/users', methods=['GET'])
def get_users():

    try:
        res = []
        for key, val in userDict.items():
            res.append(val.to_dict())

        return jsonify(res), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
@app.route('/api/user', methods=['POST'])
def generate_user():
    try:
        data = request.get_json()
        id = int(data['id'])
        name = data['name']
        user = UserEntity(id, name)
        # user.store_user(id, name)
        userDict[id] = user

        return jsonify(user.to_dict()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    

#---------------------------------------------

@app.route('/api/group', methods=['GET'])
def get_group():
    try:
        groupId = request.args.get('id')
        print(groupId)
        return jsonify(groupDict[int(groupId)].to_dict()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/groups', methods=['GET'])
def get_groups():
    try:
        res = []
        for key, val in groupDict.items():
            res.append(val.to_dict())
        return jsonify(res), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400    

@app.route('/api/group', methods=['POST'])
def generate_group():
    try:
        data = request.get_json()
        id = int(data['id'])
        name = data['name']
        group = GroupEntity(id, name, {})
        groupDict[id] = group    

        return jsonify(group.to_dict()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
#--------------------------------------------

@app.route('/api/init-user-in-group', methods=['POST'])
def init_user_in_group():
    try:
        data = request.get_json()
        userId = int(data['userId'])
        # userPermission = int(data['userPermission'])
        groupId = int(data['groupId'])
        user = userDict[userId]
        group = groupDict[groupId]

        group.add_user(user, 0)

        return jsonify(group.to_dict()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
@app.route('/api/add-user-to-group', methods=['POST'])
def add_user_to_group():
    try:
        data = request.get_json()
        userId = int(data['userId'])
        adminId = int(data['adminId'])
        groupId = int(data['groupId'])
        user = userDict[userId]
        admin = userDict[adminId]
        group = groupDict[groupId]

        if not group.user_exists(admin):
            return jsonify({"error": "Admin user not found in group"}), 400
        elif not group.user_exists(user):
            return jsonify({"error": "User not found"}), 400
        elif group.user_exists(user):
            return jsonify({"error": "User already exists in group"}), 400
        elif group.get_user_permission(adminId) == 1:
            return jsonify({"error": "User does not have permission"}), 400
        
        aes_key = fullkey(groupId, adminId)

        print("User: ", userId)
        part1, part2 = split_key(aes_key)
        store_key(part1, groupId, userId)
        group.add_user(user, part2)
        # group.set_user_key(userId, part2)
        print("Original key: ", base64.b64encode(join_key(part1, part2)).decode())  

        return jsonify(group.to_dict()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

#-------------------------------------------------

# Route to generate and split key
@app.route('/keys', methods=['POST'])
def generate_key():
    aes_key = generate_aes_key()

    data = request.get_json()
    groupId = int(data['groupId'])
    adminId = int(data['adminId'])
    group = groupDict[groupId]

    if group.get_user_permission(adminId) != 3:
        return jsonify({"error": "User does not have permission"}), 400
    
    for userId in group.keymap:
        print("User: ", userId)
        part1, part2 = split_key(aes_key)
        store_key(part1, groupId, userId)
        group.set_user_key(userId, part2)
        print("Original key: ", base64.b64encode(join_key(part1, part2)).decode())

    return jsonify({
        "message": "Keys generated successfully!",
    }), 200

# Route to encrypt a file
@app.route('/encrypt', methods=['POST'])
def encrypt():
    data = request.files['file']
    groupId = request.form.get('groupId')
    userId = request.form.get('userId')
    
    #groupID and userID    
    full_key = fullkey(groupId, userId)

    input_file = "input_file.txt"
    encrypted_file = "encrypted_file.enc"

    data.save(input_file)
    encrypt_file(input_file, encrypted_file, full_key)

    return jsonify({
        "message": "File encrypted successfully!",
        "encrypted_file": encrypted_file
    }), 200

# Route to decrypt a file
@app.route('/decrypt', methods=['POST'])
def decrypt():
    data = request.files['file']
    groupId = request.form.get('groupId')
    userId = request.form.get('userId')
    #groupID and userID
    full_key = full_key(groupId, userId)

    input_file = "uploaded_encrypted_file.enc"
    decrypted_file = "decrypted_output.txt"
    
    # Save the uploaded encrypted file
    data.save(input_file)
    decrypt_file(input_file, decrypted_file, full_key)

    return jsonify({
        "message": "File decrypted successfully!",
        "decrypted_file": decrypted_file
    }), 200

if __name__ == '__main__':
    app.run(debug=True)
