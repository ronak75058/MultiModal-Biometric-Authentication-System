# main.py

import os
import sqlite3
from database_setup import setup_database
from register_user import register_new_user
from delete_user import delete_user_data
from face_auth import face_auth
from fingerprint_auth_sim import fingerprint_auth_sim
from signature_auth import signature_auth

def get_attempt_path_from_staging(image_type):
    """Waits for the user to place an authentication attempt image in the staging folder."""
    staging_folder = os.path.join("biometric_data", "staging")
    os.makedirs(staging_folder, exist_ok=True)
    base_filename = f"attempt_{image_type}"
    
    while True:
        print("\n" + "="*50)
        print(f"ACTION REQUIRED: To authenticate, please place your {image_type} image here:")
        print(f"  -> Folder: {staging_folder}")
        print(f"  -> Name it: '{base_filename}.png' OR '{base_filename}.jpg'")
        print("="*50)
        input("After you have placed the file, press Enter to continue...")

        path_png = os.path.join(staging_folder, f"{base_filename}.png")
        path_jpg = os.path.join(staging_folder, f"{base_filename}.jpg")

        attempt_path = None
        if os.path.exists(path_png):
            attempt_path = path_png
        elif os.path.exists(path_jpg):
            attempt_path = path_jpg

        if attempt_path:
            return attempt_path
        else:
            retry = input("File not found. Do you want to (r)etry or (c)ancel? ").strip().lower()
            if retry != 'r':
                return None

def main():
    db_file = "multimodal_biometrics.db"
    setup_database(db_file)

    print("=" * 50)
    print("    Welcome to the Multimodal Biometric System")
    print("=" * 50)

    while True:
        print("\n" + "-" * 50)
        choice = input("Do you want to (r)egister, (a)uthenticate, or (d)elete a user? (q to quit): ").strip().lower()

        if choice == 'q':
            print("Thank you for using the system. Goodbye!")
            break
        
        elif choice == 'r':
            username = input("Enter a new username for registration: ").strip()
            if not username:
                print("Username cannot be empty.")
                continue
            
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users WHERE username=?", (username,))
            if cursor.fetchone():
                print(f"Error: Username '{username}' already exists.")
            else:
                register_new_user(username, db_file)
            conn.close()

        elif choice == 'd':
            username = input("Enter the username to delete: ").strip()
            confirm = input(f"Are you sure you want to permanently delete all data for '{username}'? (yes/no): ").strip().lower()
            if confirm == 'yes':
                delete_user_data(username, db_file)
            else:
                print("Deletion cancelled.")

        elif choice == 'a':
            username = input("Enter your username for authentication: ").strip()
            
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
            cursor.execute("SELECT face_data_path, fingerprint_data_path, signature_data_path FROM users WHERE username=?", (username,))
            user_data = cursor.fetchone()
            conn.close()

            if not user_data:
                print(f"Error: User '{username}' not found.")
                continue

            face_path, fingerprint_path, signature_path = user_data
            
            print("\nChoose an authentication method:")
            if face_path: print("  (f)ace")
            if fingerprint_path: print("  (p)rint (fingerprint)")
            if signature_path: print("  (s)ignature")

            auth_choice = input("Your choice: ").strip().lower()
            
            authenticated = False
            if auth_choice == 'f' and face_path:
                authenticated = face_auth(username)
            elif auth_choice == 'p' and fingerprint_path:
                attempt_path = get_attempt_path_from_staging("fingerprint")
                if attempt_path:
                    authenticated = fingerprint_auth_sim(username, db_file, attempt_path)
                    # --- CHANGE HERE: Clean up the staging file ---
                    try:
                        os.remove(attempt_path)
                        print(f"Cleaned up staging file: {os.path.basename(attempt_path)}")
                    except OSError as e:
                        print(f"Error cleaning up staging file: {e}")
            elif auth_choice == 's' and signature_path:
                attempt_path = get_attempt_path_from_staging("signature")
                if attempt_path:
                    authenticated = signature_auth(username, db_file, attempt_path)
                    # --- CHANGE HERE: Clean up the staging file ---
                    try:
                        os.remove(attempt_path)
                        print(f"Cleaned up staging file: {os.path.basename(attempt_path)}")
                    except OSError as e:
                        print(f"Error cleaning up staging file: {e}")
            else:
                print("Invalid choice.")
                continue

            print("\n--- Authentication Result ---")
            if authenticated:
                print(f"Welcome, {username}! Access Granted. ✅")
            else:
                print("Access Denied. ❌")
        else:
            print("Invalid command. Please choose 'r', 'a', 'd', or 'q'.")

if __name__ == "__main__":
    main()