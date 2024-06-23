#!/data/data/com.termux/files/usr/bin/python

import os
import base64
import json
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend

KEY_FILE = "key.json"

def generate_key():
    return os.urandom(32)  # 256-bit key for AES

def save_key(key):
    with open(KEY_FILE, "w") as f:
        json.dump({"key": base64.b64encode(key).decode()}, f)

def load_key():
    if not os.path.exists(KEY_FILE):
        key = generate_key()
        save_key(key)
    else:
        with open(KEY_FILE, "r") as f:
            key = base64.b64decode(json.load(f)["key"])
    return key

def export_key(file_path):
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, "r") as f:
            key_data = f.read()
        with open(file_path, "w") as f:
            f.write(key_data)
        print(f"Key exported to {file_path}")
    else:
        print("No key found to export.")

def import_key(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            key_data = f.read()
        with open(KEY_FILE, "w") as f:
            f.write(key_data)
        print(f"Key imported from {file_path}")
    else:
        print(f"No key file found at {file_path}")

def pad_text(text):
    padder = padding.PKCS7(algorithms.AES.block_size).padder()
    padded_data = padder.update(text.encode()) + padder.finalize()
    return padded_data

def unpad_text(padded_text):
    unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
    data = unpadder.update(padded_text) + unpadder.finalize()
    return data.decode()

def encrypt_text(text, key):
    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    padded_text = pad_text(text)
    encrypted_text = encryptor.update(padded_text) + encryptor.finalize()
    return base64.b64encode(iv + encrypted_text).decode()

def decrypt_text(encrypted_text, key):
    encrypted_text = base64.b64decode(encrypted_text)
    iv = encrypted_text[:16]
    encrypted_text = encrypted_text[16:]
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    decrypted_padded_text = decryptor.update(encrypted_text) + decryptor.finalize()
    return unpad_text(decrypted_padded_text)

def main():
    print("Welcome to the Encryption/Decryption Tool")
    key = load_key()
    
    while True:
        print("\nOptions:")
        print("1. Encrypt Text")
        print("2. Decrypt Text")
        print("3. Export Key")
        print("4. Import Key")
        print("5. Exit")
        
        choice = input("Select an option: ")
        
        if choice == "1":
            text = input("Enter text to encrypt: ")
            encrypted_text = encrypt_text(text, key)
            print(f"Encrypted Text: {encrypted_text}")
        elif choice == "2":
            encrypted_text = input("Enter text to decrypt: ")
            try:
                decrypted_text = decrypt_text(encrypted_text, key)
                print(f"Decrypted Text: {decrypted_text}")
            except Exception as e:
                print(f"Error decrypting text: {e}")
        elif choice == "3":
            file_path = input("Enter file path to export the key: ")
            export_key(file_path)
        elif choice == "4":
            file_path = input("Enter file path to import the key: ")
            import_key(file_path)
        elif choice == "5":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()