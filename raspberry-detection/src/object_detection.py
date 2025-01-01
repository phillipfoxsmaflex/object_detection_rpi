# -*- coding: utf-8 -*-
from ultralytics import YOLO
import cv2
import numpy as np
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ObjectDetector:
    def __init__(self, model_path, conf_threshold=0.25):
        try:
            logger.info(f"Loading YOLO model from {model_path}")
            self.model = YOLO(model_path)
            self.conf_threshold = conf_threshold
            logger.info("Model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load model: {str(e)}")
            raise
    
    def detect(self, frame):
        try:
            if frame is None:
                logger.error("Received empty frame")
                return None, {}
                
            #  Objekterkennung durch
            results = self.model(frame, conf=self.conf_threshold)
            
            # Extrahiere Detektionen
            detections = {}
            for r in results:
                boxes = r.boxes
                for box in boxes:
                    cls = int(box.cls[0])
                    conf = float(box.conf[0])
                    label = self.model.names[cls]
                    
                    if label not in detections:
                        detections[label] = {
                            "count": 1,
                            "confidences": [conf]
                        }
                    else:
                        detections[label]["count"] += 1
                        detections[label]["confidences"].append(conf)
            
            # Erstelle annotiertes Frame
            annotated_frame = results[0].plot()
            
            return annotated_frame, detections
            
        except Exception as e:
            logger.error(f"Detection error: {str(e)}")
            return None, {}
