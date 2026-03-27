import face_recognition
from PIL import Image
import numpy as np

# Create image
img = Image.new('RGB', (100, 100), color = 'red')
img.save('test_pil.jpg')
loaded_img = face_recognition.load_image_file("test_pil.jpg")

print("Testing landmarks...")
try:
    landmarks = face_recognition.face_landmarks(loaded_img)
    print(f"Landmarks success. Found {len(landmarks)} faces (expected 0 but fn works)")
except Exception as e:
    print(f"Landmarks failed: {e}")
