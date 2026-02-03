import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# We add both the main folder AND the internal folder to be 100% sure
paths_to_add = [
    os.path.join(BASE_DIR, "EgoBlur"),
    os.path.join(BASE_DIR, "EgoBlur", "egoblur")
]

for p in paths_to_add:
    if p not in sys.path:
        sys.path.insert(0, p)

try:
    import torch
    import cv2
    # This reaches for the interface.py file you just updated
    from egoblur.interface import DetectorIterative
    
    print("\n" + "✅" * 10)
    print("SUCCESS: ALL LINKS ESTABLISHED!")
    print("Python has successfully mapped the Meta EgoBlur Gen2 library.")
    print("✅" * 10)

except ImportError as e:
    print(f"\n❌ LINK FAILED: {e}")
    print("Debug Info: Python is currently looking in these paths:")
    for p in sys.path[:3]:
        print(f" - {p}")