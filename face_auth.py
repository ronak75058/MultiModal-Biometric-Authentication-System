# face_auth.py

import cv2
import face_recognition
import os
import time
import numpy as np


def face_auth(username):
    """
    Authenticates a user by comparing their live face against 5 registered images
    using average face distance for higher accuracy.
    """

    known_face_encodings = []
    base_folder = os.path.join("biometric_data", "faces")

    if not os.path.exists(base_folder):
        print(f"Error: Biometric data folder not found at {base_folder}")
        return False

    # Load registered face images
    for i in range(1, 6):
        image_path = os.path.join(base_folder, f"{username}_{i}.jpg")

        if os.path.exists(image_path):
            try:
                registered_image = face_recognition.load_image_file(image_path)
                encoding = face_recognition.face_encodings(registered_image)[0]
                known_face_encodings.append(encoding)
            except IndexError:
                print(f"Warning: Could not find a face in registered image {image_path}. Skipping.")
        else:
            print(f"Warning: Registered image {image_path} not found.")

    if len(known_face_encodings) < 3:
        print("Could not load enough valid registered face encodings. Authentication failed.")
        return False

    # Open webcam
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return False

    print("\nStarting face authentication...")
    print("Please look at the camera. You have 10 seconds.")

    start_time = time.time()
    authentication_successful = False

    while time.time() - start_time < 10:
        ret, frame = cap.read()
        if not ret:
            break

        face_locations = face_recognition.face_locations(frame)
        face_encodings = face_recognition.face_encodings(frame, face_locations)

        for face_encoding, face_location in zip(face_encodings, face_locations):
            face_distances = face_recognition.face_distance(
                known_face_encodings, face_encoding
            )
            average_distance = np.mean(face_distances)

            top, right, bottom, left = face_location
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

            TOLERANCE = 0.5

            if average_distance < TOLERANCE:
                text = "Authenticated!"
                cv2.putText(
                    frame, text, (left, bottom + 25),
                    cv2.FONT_HERSHEY_DUPLEX, 0.8, (0, 255, 0), 2
                )
                authentication_successful = True
            else:
                text = f"Dist: {average_distance:.2f}"
                cv2.putText(
                    frame, text, (left, bottom + 25),
                    cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 1
                )

        cv2.imshow("Authentication - Press 'q' to quit", frame)

        if cv2.waitKey(1) & 0xFF == ord('q') or authentication_successful:
            break

    if authentication_successful:
        print("\nFace recognized! Authentication successful.")
    else:
        print("\nAuthentication timed out or face did not match.")

    cap.release()
    cv2.destroyAllWindows()

    return authentication_successful