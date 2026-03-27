import face_recognition
import cv2
import numpy as np
import dlib

print(f"Dlib version: {dlib.__version__}")
print(f"Face Recognition version: {face_recognition.__version__}")

# Create valid image
img = np.zeros((200, 200, 3), dtype=np.uint8)
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

print("Testing grayscale numpy array...")
try:
    face_recognition.face_encodings(gray)
    print("Success with grayscale")
except Exception as e:
    print(f"Failed grayscale: {e}")

print("Testing RGB numpy array...")
try:
    rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    face_recognition.face_encodings(rgb)
    print("Success with RGB")
except Exception as e:
    print(f"Failed RGB: {e}")
