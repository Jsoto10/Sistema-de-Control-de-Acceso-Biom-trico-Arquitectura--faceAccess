import face_recognition
import cv2
import numpy as np

# Create valid image
img = np.zeros((100, 100, 3), dtype=np.uint8)
cv2.imwrite("test.jpg", img)

print("Testing load_image_file...")
try:
    loaded = face_recognition.load_image_file("test.jpg")
    print(f"Loaded shape: {loaded.shape}")
    encs = face_recognition.face_encodings(loaded)
    print("Success with load_image_file")
except Exception as e:
    print(f"Failed with load_image_file: {e}")
