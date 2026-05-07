# signature_auth.py

import cv2
import sqlite3
import os
from skimage.metrics import structural_similarity as ssim

def preprocess_signature(image_path):
    """
    Loads and preprocesses a signature image for comparison.
    """
    try:
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if img is None: return None
        
        # Invert and apply binary threshold to isolate the signature
        _, thresh = cv2.threshold(img, 128, 255, cv2.THRESH_BINARY_INV)
        
        # Find contours and crop to the signature's bounding box
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours: return None
        
        x, y, w, h = cv2.boundingRect(max(contours, key=cv2.contourArea))
        cropped = thresh[y:y+h, x:x+w]
        return cropped
    except Exception as e:
        print(f"Error processing signature image {image_path}: {e}")
        return None

def signature_auth(username, db_file, attempt_image_path, threshold=0.6):
    """
    Compares a user's signature with their registered one using SSIM.
    This version handles its own database lookup.
    """
    # --- Get Registered Signature ---
    conn = None # Initialize conn to None
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        cursor.execute("SELECT signature_data_path FROM users WHERE username=?", (username,))
        result = cursor.fetchone()
        if not result or not result[0] or not os.path.exists(result[0]):
            print("No registered signature found.")
            return False
        registered_sig_path = result[0]
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False
    finally:
        if conn:
            conn.close()

    # --- Preprocess Signatures ---
    registered_sig = preprocess_signature(registered_sig_path)
    attempt_sig = preprocess_signature(attempt_image_path)
    
    if registered_sig is None or attempt_sig is None:
        print("Could not process one or both signature images.")
        return False

    # --- Compare ---
    # Resize attempt to match registered signature size for accurate comparison
    try:
        attempt_sig_resized = cv2.resize(attempt_sig, (registered_sig.shape[1], registered_sig.shape[0]))
    except cv2.error:
        print("Signatures have incompatible shapes. Authentication failed.")
        return False

    # Calculate Structural Similarity
    (score, _) = ssim(registered_sig, attempt_sig_resized, full=True)

    print(f"Signature Similarity Score: {score:.4f}")
    
    if score >= threshold:
        print("Signatures match. Authentication successful.")
        return True
    else:
        print("Signatures do not match. Authentication failed.")
        return False