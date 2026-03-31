import cv2
import face_recognition
import os

def verify_face(aadhaar):

    folder = "faces"

    known_encodings = []

    # Load all saved images
    for file in os.listdir(folder):
        if file.startswith(aadhaar):
            img_path = os.path.join(folder, file)

            image = face_recognition.load_image_file(img_path)
            encodings = face_recognition.face_encodings(image)

            if len(encodings) > 0:
                known_encodings.append(encodings[0])

    if len(known_encodings) == 0:
        print("No registered face found")
        return False

    # Open camera
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # FIX camera issue

    if not cap.isOpened():
        print("Camera not opening")
        return False

    print("Press SPACE to verify")

    while True:
        ret, frame = cap.read()

        if not ret:
            continue

        cv2.imshow("Verify Face", frame)

        key = cv2.waitKey(1)

        if key == 32:  # SPACE

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            face_locations = face_recognition.face_locations(rgb)

            if len(face_locations) == 0:
                print("No face detected")
                continue

            face_encodings = face_recognition.face_encodings(rgb, face_locations)

            if len(face_encodings) == 0:
                print("Encoding failed")
                continue

            # Compare with all saved images
            for known in known_encodings:
                match = face_recognition.compare_faces([known], face_encodings[0], tolerance=0.5)

                if match[0]:
                    print("Face Matched")
                    cap.release()
                    cv2.destroyAllWindows()
                    return True

            print("Face Not Matched")

        elif key == 27:  # ESC
            break

    cap.release()
    cv2.destroyAllWindows()
    return False