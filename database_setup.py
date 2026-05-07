import sqlite3
import os

def setup_database(db_file):
    """
    Sets up the SQLite database and creates necessary directories for biometric data.
    """
    # --- Create Directories ---
    # Base directory for all data
    base_data_dir = "biometric_data"
    
    # Subdirectories for each biometric type and staging
    required_dirs = [
        "faces",
        "fingerprints",
        "signatures",
        "staging"  # For temporary user-provided images
    ]

    # Create the base directory if it doesn't exist
    os.makedirs(base_data_dir, exist_ok=True)
    
    # Create each subdirectory
    for dir_name in required_dirs:
        os.makedirs(os.path.join(base_data_dir, dir_name), exist_ok=True)

    # --- Create Database and Table ---
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()

        # Create the 'users' table if it doesn't already exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                face_data_path TEXT,
                fingerprint_data_path TEXT,
                signature_data_path TEXT
            );
        """)
        conn.commit()
        # This print statement is commented out to keep the main UI cleaner
        # print(f"Database '{db_file}' and required directories are set up.")

    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    # This allows the script to be run directly to set up the environment
    db_file = "multimodal_biometrics.db"
    setup_database(db_file)
    print("Database and directory setup complete.")

