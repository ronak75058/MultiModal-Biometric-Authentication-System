import cv2
import os
import sqlite3
from skimage.metrics import structural_similarity as ssim

def preprocess_image(image_path):
    """Loads an image, converts to grayscale, and applies thresholding."""
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if image is None:
        return None
    # Apply a binary threshold to get a clear black and white image
    _, thresholded = cv2.threshold(image, 128, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)
    return thresholded

def fingerprint_auth_sim(username, db_file, attempt_image_path):
    """
    Simulates fingerprint authentication by comparing the structural similarity
    of the attempt image with the user's registered fingerprint image.
    """
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("SELECT fingerprint_data_path FROM users WHERE username=?", (username,))
    result = cursor.fetchone()
    conn.close()

    if not result or not result[0]:
        print("No fingerprint data registered for this user.")
        return False

    registered_fingerprint_path = result[0]

    if not os.path.exists(registered_fingerprint_path):
        print(f"Error: Registered fingerprint file not found at {registered_fingerprint_path}")
        return False
        
    if not os.path.exists(attempt_image_path):
        print(f"Error: Attempt fingerprint file not found at {attempt_image_path}")
        return False

    # --- Preprocess both images for accurate comparison ---
    registered_image = preprocess_image(registered_fingerprint_path)
    attempt_image = preprocess_image(attempt_image_path)
    
    if registered_image is None or attempt_image is None:
        print("Error processing one of the fingerprint images.")
        return False

    # Resize attempt image to match the registered one
    h, w = registered_image.shape
    attempt_image_resized = cv2.resize(attempt_image, (w, h))

    # --- Compare using Structural Similarity (SSIM) ---
    score, _ = ssim(registered_image, attempt_image_resized, full=True)
    
    print(f"Fingerprint similarity score: {score:.2f}")

    # Set a threshold for what is considered a match
    threshold = 0.6
    if score >= threshold:
        return True
    else:
        return False

