import sqlite3
import os
import glob

def delete_user_data(username, db_file):
    """
    Deletes a user's record and all associated biometric files.
    """
    print(f"\n--- Deleting User: {username} ---")
    
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()

        # 1. Find the user and their file paths from the database
        cursor.execute("SELECT face_data_path, fingerprint_data_path, signature_data_path FROM users WHERE username=?", (username,))
        result = cursor.fetchone()

        if not result:
            print(f"Error: User '{username}' not found in the database.")
            return

        face_ref_path, fingerprint_path, signature_path = result
        
        # --- 2. Delete all biometric files from the disk ---

        # Delete all 5 face images
        base_folder = os.path.dirname(face_ref_path)
        image_pattern = os.path.join(base_folder, f"{username}_*.jpg")
        face_files = glob.glob(image_pattern)
        
        if not face_files:
            print(f"Warning: No face files found for {username}, but continuing with deletion.")
        else:
            for f in face_files:
                try:
                    os.remove(f)
                    print(f"Deleted face file: {f}")
                except OSError as e:
                    print(f"Error deleting file {f}: {e}")

        # Delete fingerprint file
        if fingerprint_path and os.path.exists(fingerprint_path):
            try:
                os.remove(fingerprint_path)
                print(f"Deleted fingerprint file: {fingerprint_path}")
            except OSError as e:
                print(f"Error deleting file {fingerprint_path}: {e}")

        # Delete signature file
        if signature_path and os.path.exists(signature_path):
            try:
                os.remove(signature_path)
                print(f"Deleted signature file: {signature_path}")
            except OSError as e:
                print(f"Error deleting file {signature_path}: {e}")

        # --- 3. Delete the user record from the database ---
        cursor.execute("DELETE FROM users WHERE username=?", (username,))
        conn.commit()

        print(f"\nSuccessfully deleted all data for user '{username}'.")

    except sqlite3.Error as e:
        print(f"Database error during deletion: {e}")
    finally:
        if conn:
            conn.close()
