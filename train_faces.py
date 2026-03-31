import cv2
import os
import numpy as np

path = "faces"

recognizer = cv2.face.LBPHFaceRecognizer_create()

faces = []
labels = []
label_map = {}
current_label = 0

for file in os.listdir(path):

    img_path = os.path.join(path, file)

    label = file.split("_")[0]

    if label not in label_map:
        label_map[label] = current_label
        current_label += 1

    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)

    faces.append(img)
    labels.append(label_map[label])

recognizer.train(faces, np.array(labels))

recognizer.save("trainer.yml")

print("Training completed")