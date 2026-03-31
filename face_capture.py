import cv2
import os
import time

def capture_face(aadhaar):

    folder = "faces"

    if not os.path.exists(folder):
        os.makedirs(folder)

    cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # FIX camera issue

    if not cam.isOpened():
        print("Camera not working")
        return False

    count = 0
    print("Capturing 5 images... Look at camera")

    while count < 5:
        ret, frame = cam.read()

        if not ret:
            continue

        cv2.imshow("Capture Face", frame)

        # save image
        img_path = os.path.join(folder, f"{aadhaar}_{count}.jpg")
        cv2.imwrite(img_path, frame)

        print("Saved:", img_path)
        count += 1

        time.sleep(1)  # wait 1 sec

        if cv2.waitKey(1) & 0xFF == 27:
            break

    cam.release()
    cv2.destroyAllWindows()

    return True