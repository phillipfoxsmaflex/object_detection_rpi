# -*- coding: utf-8 -*-
from camera import Camera
import time
import cv2

def test_camera():
    try:
        print("Starting camera test...")
        cam = Camera()
        
        for i in range(5):
            print(f"Capturing frame {i+1}...")
            frame = cam.get_frame()
            if frame is not None:
                print(f"Frame {i+1} captured: shape={frame.shape}")
                # Frame als Bild speichern
                cv2.imwrite(f"test_frame_{i+1}.jpg", cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
            else:
                print(f"Failed to capture frame {i+1}")
            time.sleep(1)
            
        cam.release()
        print("Camera test completed successfully")
        
    except Exception as e:
        print(f"Camera test failed: {str(e)}")

if __name__ == "__main__":
    test_camera()