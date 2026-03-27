import face_recognition
from PIL import Image
import numpy as np

# Create valid image using PIL
img = Image.new('RGB', (100, 100), color = 'red')
img.save('test_pil.jpg')

print("Testing PIL image...")
try:
    # Load using PIL (which face_recognition uses internally usually)
    loaded_img = face_recognition.load_image_file("test_pil.jpg")
    print(f"Loaded shape: {loaded_img.shape} dtype: {loaded_img.dtype}")
    
    # Force C-contiguous just in case, though load_image_file should handle it
    loaded_img = np.ascontiguousarray(loaded_img)
    
    encs = face_recognition.face_encodings(loaded_img)
    print("Success with PIL")
except Exception as e:
    print(f"Failed with PIL: {e}")
