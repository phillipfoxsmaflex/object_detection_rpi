# -*- coding: utf-8 -*-
from picamera2 import Picamera2
import cv2
import numpy as np
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Camera:
    def __init__(self):
        try:
            logger.info("Initializing camera...")
            self.camera = Picamera2()
            
            # Warten auf Kamera-Initialisierung
            time.sleep(2)
            
            # Konfiguration  Preview
            preview_config = self.camera.create_preview_configuration(
                main={"size": (640, 480), "format": "RGB888"},
                buffer_count=2
            )
            
            # Konfiguration anwenden
            self.camera.configure(preview_config)
            
            # Kamera starten
            self.camera.start()
            logger.info("Camera started successfully")
            
            # Weitere Wartezeit Sensor-Stabilisierung
            time.sleep(2)
            
            # Test-Frame aufnehmen
            test_frame = self.camera.capture_array()
            if test_frame is not None:
                logger.info(f"Test frame captured successfully: shape={test_frame.shape}")
            else:
                raise Exception("Failed to capture test frame")
                
        except Exception as e:
            logger.error(f"Camera initialization failed: {str(e)}")
            raise RuntimeError(f"Failed to initialize camera: {str(e)}")
    
    def get_frame(self):
        try:
            if not hasattr(self, 'camera'):
                logger.error("Camera not initialized")
                return None
            
            frame = self.camera.capture_array()
            if frame is None:
                logger.error("Failed to capture frame")
                return None
            
            # Frame-Format 
            if len(frame.shape) == 2:  # Grayscale
                frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2RGB)
            elif frame.shape[2] == 4:  # RGBA
                frame = cv2.cvtColor(frame, cv2.COLOR_RGBA2RGB)
            
            logger.debug(f"Frame captured successfully: shape={frame.shape}")
            return frame
            
        except Exception as e:
            logger.error(f"Error capturing frame: {str(e)}")
            return None
    
    def release(self):
        try:
            if hasattr(self, 'camera'):
                self.camera.stop()
                logger.info("Camera stopped successfully")
        except Exception as e:
            logger.error(f"Error stopping camera: {str(e)}")
