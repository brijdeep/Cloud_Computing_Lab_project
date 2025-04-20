from flask import Flask, request, jsonify
from key_manager import generate_aes_key, split_key, store_key, join_key, get_key
from encrypt_decrypt import encrypt_file, decrypt_file
import base64
import os
from UserEntity import UserEntity
from GroupEntity import GroupEntity, create_group
from s3_utils import upload_to_s3, download_from_s3  # this should contain your boto3 S3 logic
from flask import send_file


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
    try:
        uploaded_file = request.files['file']
        groupId = int(request.form.get('groupId'))
        userId = int(request.form.get('userId'))

        # Derive full AES key
        key = fullkey(groupId, userId)

        # File paths
        input_path = f"uploads/input_{userId}.txt"
        encrypted_path = f"uploads/encrypted_{userId}.enc"

        # Save uploaded file locally
        uploaded_file.save(input_path)

        # Encrypt file
        encrypt_file(input_path, encrypted_path, key)

        # Unique S3 key per user/group
        s3_key = f"encrypted-files/group-{groupId}/user-{userId}.enc"

        # Upload to S3
        upload_to_s3(encrypted_path, s3_key)

        # Optionally delete local files
        os.remove(input_path)
        os.remove(encrypted_path)

        return jsonify({
            "message": "File encrypted and uploaded successfully!",
            "s3_key": s3_key
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400


# Route to decrypt a file
@app.route('/decrypt', methods=['POST'])
def decrypt():
    try:
        groupId = int(request.form.get('groupId'))
        userId = int(request.form.get('userId'))
        s3_key = request.form.get('s3_key')

        # Derive full AES key
        key = fullkey(groupId, userId)

        # Local file paths
        encrypted_path = f"uploads/encrypted_{userId}.enc"
        decrypted_path = f"uploads/decrypted_{userId}.txt"

        # Download encrypted file from S3
        download_from_s3(s3_key, encrypted_path)

        # Decrypt
        decrypt_file(encrypted_path, decrypted_path, key)

        # Optionally delete encrypted file
        os.remove(encrypted_path)



        return send_file(decrypted_path, as_attachment=True)


        return jsonify({
            "message": "File decrypted successfully!",
            "decrypted_file": decrypted_path  # or read content and return if needed
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400


if __name__ == '__main__':
    app.run(debug=True)
