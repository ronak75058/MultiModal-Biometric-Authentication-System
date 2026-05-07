import cv2
import os
import sqlite3
import shutil
import time

def capture_multiple_faces(username):
    """Captures 5 face images from the webcam with on-screen instructions."""
    base_folder = os.path.join("biometric_data", "faces")
    os.makedirs(base_folder, exist_ok=True)
    
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return None

    instructions = [
        "Look STRAIGHT at the camera",
        "Slowly turn your head to the LEFT",
        "Slowly turn your head to the RIGHT",
        "Slowly tilt your head UP",
        "Slowly tilt your head DOWN"
    ]
    
    face_paths = []
    for i, instruction in enumerate(instructions):
        img_path = os.path.join(base_folder, f"{username}_{i+1}.jpg")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Error: Can't receive frame. Exiting ...")
                break

            # Display instructions on the frame
            cv2.putText(frame, f"Image {i+1}/5: {instruction}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame, "Press 'c' to capture, 'q' to quit", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.imshow('Face Registration', frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('c'):
                cv2.imwrite(img_path, frame)
                print(f"Image {i+1} saved to {img_path}")
                face_paths.append(img_path)
                # Brief pause to show feedback
                cv2.putText(frame, "SAVED!", (200, 250), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3)
                cv2.imshow('Face Registration', frame)
                cv2.waitKey(1000)
                break
            elif key == ord('q'):
                print("Registration cancelled by user.")
                cap.release()
                cv2.destroyAllWindows()
                return None
    
    cap.release()
    cv2.destroyAllWindows()
    
    return face_paths

def get_image_from_staging(image_type, username):
    """Waits for the user to place an image in the staging folder."""
    staging_folder = os.path.join("biometric_data", "staging")
    os.makedirs(staging_folder, exist_ok=True)

    base_filename = f"{username}_{image_type}"
    
    while True:
        print("\n" + "="*50)
        print(f"ACTION REQUIRED: Please place your {image_type} image in the staging folder.")
        print(f"  -> Folder: {staging_folder}")
        print(f"  -> Name it: '{base_filename}.png' OR '{base_filename}.jpg'")
        print("="*50)
        input("After you have placed and named the file correctly, press Enter to continue...")

        # Check for both .png and .jpg
        path_png = os.path.join(staging_folder, f"{base_filename}.png")
        path_jpg = os.path.join(staging_folder, f"{base_filename}.jpg")
        path_jpg = os.path.join(staging_folder, f"{base_filename}.jpeg")

        if os.path.exists(path_png):
            print(f"File '{base_filename}.png' found! Proceeding.")
            return path_png
        elif os.path.exists(path_jpg):
            print(f"File '{base_filename}.jpg' found! Proceeding.")
            return path_jpg
        else:
            retry = input("File not found in the staging folder.\nDo you want to (r)etry or (c)ancel? ").strip().lower()
            if retry != 'r':
                return None

def register_new_user(username, db_file):
    """Guides a user through the full registration process for available biometrics."""
    print("Please provide the following biometric data.")

    # --- 1. Face Registration (Mandatory) ---
    print("\n--- Face Registration (Multi-Image) ---")
    face_paths = capture_multiple_faces(username)
    if not face_paths:
        print("Registration failed: Face capture is required.")
        return
    face_data_path_ref = face_paths[0]

    # --- 2. Fingerprint Registration (Optional & Manual) ---
    fingerprint_path_dest = None
    choice = input("\nDo you want to register a fingerprint? (yes/no): ").strip().lower()
    if choice == 'yes':
        staged_fingerprint_path = get_image_from_staging("fingerprint", username)
        if staged_fingerprint_path:
            _, ext = os.path.splitext(staged_fingerprint_path)
            dest_folder = os.path.join("biometric_data", "fingerprints")
            os.makedirs(dest_folder, exist_ok=True)
            fingerprint_path_dest = os.path.join(dest_folder, f"{username}{ext}")
            shutil.move(staged_fingerprint_path, fingerprint_path_dest)
            print(f"Fingerprint saved to {fingerprint_path_dest}")
        else:
            print("Fingerprint registration cancelled.")

    # --- 3. Signature Registration (Optional & Manual) ---
    signature_path_dest = None
    choice = input("\nDo you want to register a signature? (yes/no): ").strip().lower()
    if choice == 'yes':
        staged_sig_path = get_image_from_staging("signature", username)
        if staged_sig_path:
            _, ext = os.path.splitext(staged_sig_path)
            dest_folder = os.path.join("biometric_data", "signatures")
            os.makedirs(dest_folder, exist_ok=True)
            signature_path_dest = os.path.join(dest_folder, f"{username}{ext}")
            shutil.move(staged_sig_path, signature_path_dest)
            print(f"Signature saved to {signature_path_dest}")
        else:
            print("Signature registration cancelled.")

    # --- 4. Save to Database ---
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO users (username, face_data_path, fingerprint_data_path, signature_data_path)
            VALUES (?, ?, ?, ?)
        """, (username, face_data_path_ref, fingerprint_path_dest, signature_path_dest))
        conn.commit()
        print(f"\nUser '{username}' successfully registered!")
    except sqlite3.Error as e:
        print(f"Database error during registration: {e}")
    finally:
        if conn:
            conn.close()

