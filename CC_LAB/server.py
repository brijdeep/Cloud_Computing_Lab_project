from flask import Flask, request, jsonify
from key_manager import generate_aes_key, split_key, store_key
from encrypt_decrypt import encrypt_file, decrypt_file
import base64
import os

app = Flask(__name__)

# Route to generate and split key
@app.route('/generate-key', methods=['POST'])
def generate_key():
    aes_key = generate_aes_key()
    part1, part2 = split_key(aes_key)

    # Store Part 1 in MongoDB
    store_key(part1)

    # Return Part 2 to the user
    return jsonify({
        "message": "Key generated successfully!",
        "part2": base64.b64encode(part2).decode()  # Send Part 2 to the user
    }), 200

# Route to encrypt a file
@app.route('/encrypt', methods=['POST'])
def encrypt():
    data = request.files['file']
    part1 = base64.b64decode(request.form['part1'])
    part2 = base64.b64decode(request.form['part2'])

    # Reconstruct the full key
    # full_key = part1 ^ part2
    full_key = bytes(a ^ b for a,b in zip(part1, part2))

    input_file = "input_file.txt"
    encrypted_file = "encrypted_file.enc"
    
    # Save the uploaded file
    data.save(input_file)

    # Encrypt the file
    encrypt_file(input_file, encrypted_file, full_key)

    return jsonify({
        "message": "File encrypted successfully!",
        "encrypted_file": encrypted_file
    }), 200

# Route to decrypt a file
@app.route('/decrypt', methods=['POST'])
def decrypt():
    data = request.files['file']
    part1 = base64.b64decode(request.form['part1'])
    part2 = base64.b64decode(request.form['part2'])

    # Reconstruct the full key
    full_key = bytes(a ^ b for a,b in zip(part1, part2))

    input_file = "uploaded_encrypted_file.enc"
    decrypted_file = "decrypted_output.txt"
    
    # Save the uploaded encrypted file
    data.save(input_file)

    # Decrypt the file
    decrypt_file(input_file, decrypted_file, full_key)

    return jsonify({
        "message": "File decrypted successfully!",
        "decrypted_file": decrypted_file
    }), 200

if __name__ == '__main__':
    app.run(debug=True)
