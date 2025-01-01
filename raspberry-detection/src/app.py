# -*- coding: utf-8 -*-
import gradio as gr
import json
import time
from camera import Camera
from mqtt_client import MQTTClient
from object_detection import ObjectDetector

class DetectionApp:
    def __init__(self):
        self.load_config()
        self.camera = None
        self.mqtt_client = None
        self.detector = None
        self.is_running = False
        
    def load_config(self):
        try:
            with open('config/settings.json', 'r') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            self.config = {
                "mqtt_broker": "localhost",
                "mqtt_port": 1883,
                "mqtt_topic": "detections",
                "model_path": "models/yolov8n.pt",
                "conf_threshold": 0.25
            }
            self.save_config()
    
    def save_config(self):
        with open('config/settings.json', 'w') as f:
            json.dump(self.config, f, indent=4)
    
    def save_settings(self, broker, port, topic, model_path, conf):
        try:
            self.config["mqtt_broker"] = broker
            self.config["mqtt_port"] = int(port)
            self.config["mqtt_topic"] = topic
            self.config["model_path"] = model_path
            self.config["conf_threshold"] = float(conf)
            self.save_config()
            return "Settings saved successfully!"
        except Exception as e:
            return f"Error saving settings: {str(e)}"
    
    def start_detection(self):
        try:
            if not self.is_running:
                print("Initializing camera...")
                try:
                    self.camera = Camera()
                    time.sleep(2)  # Wait for camera initialization
                    
                    # Capture test frame
                    test_frame = self.camera.get_frame()
                    if test_frame is None:
                        raise Exception("Could not capture test frame")
                    print("Camera initialized successfully")
                    
                    print("Initializing MQTT client...")
                    self.mqtt_client = MQTTClient(
                        self.config["mqtt_broker"],
                        self.config["mqtt_port"],
                        self.config["mqtt_topic"]
                    )
                    
                    print("Initializing object detector...")
                    self.detector = ObjectDetector(
                        self.config["model_path"],
                        self.config["conf_threshold"]
                    )
                    
                    self.mqtt_client.connect()
                    self.is_running = True
                    print("Initialization complete")
                    
                    # Return first frame
                    return self.process_frame()
                
                except Exception as e:
                    self.is_running = False
                    error_msg = f"Initialization failed: {str(e)}"
                    print(error_msg)
                    return None, error_msg
            
            return self.process_frame()
            
        except Exception as e:
            print(f"Error in start_detection: {str(e)}")
            return None, f"Error: {str(e)}"
    
    def process_frame(self):
        if not self.is_running or self.camera is None:
            return None, "Camera not initialized"
        
        print("Getting frame from camera...")
        frame = self.camera.get_frame()
        if frame is None:
            return None, "Failed to capture frame"
        
        print("Performing object detection...")
        annotated_frame, detections = self.detector.detect(frame)
        if self.mqtt_client:
            self.mqtt_client.publish_detections(detections)
        
        detection_text = "Detected Objects:\n"
        for obj, data in detections.items():
            avg_conf = sum(data["confidences"]) / len(data["confidences"])
            detection_text += f"- {obj}: {data['count']}x (Confidence: {avg_conf:.2f})\n"
        
        return annotated_frame, detection_text
    
    def stop_detection(self):
        try:
            if self.is_running:
                if self.camera:
                    self.camera.release()
                if self.mqtt_client:
                    self.mqtt_client.disconnect()
                self.camera = None
                self.mqtt_client = None
                self.detector = None
                self.is_running = False
            return "Object detection stopped"
        except Exception as e:
            print(f"Error in stop_detection: {str(e)}")
            return f"Error stopping detection: {str(e)}"
    
    def update_threshold(self, conf):
        try:
            if self.detector:
                self.detector.conf_threshold = float(conf)
            return f"Confidence threshold set to {conf}"
        except Exception as e:
            return f"Error updating threshold: {str(e)}"
    
    def create_ui(self):
        with gr.Blocks() as ui:
            with gr.Tab("Settings"):
                with gr.Row():
                    mqtt_broker = gr.Textbox(
                        label="MQTT Broker",
                        value=self.config["mqtt_broker"]
                    )
                    mqtt_port = gr.Number(
                        label="MQTT Port",
                        value=self.config["mqtt_port"]
                    )
                    mqtt_topic = gr.Textbox(
                        label="MQTT Topic",
                        value=self.config["mqtt_topic"]
                    )
                with gr.Row():
                    model_path = gr.Textbox(
                        label="Model Path",
                        value=self.config["model_path"]
                    )
                    conf_threshold = gr.Slider(
                        minimum=0.1,
                        maximum=1.0,
                        value=self.config["conf_threshold"],
                        label="Default Confidence Threshold"
                    )
                save_btn = gr.Button("Save Settings")
                save_output = gr.Textbox(label="Status")
                save_btn.click(
                    fn=self.save_settings,
                    inputs=[mqtt_broker, mqtt_port, mqtt_topic, 
                           model_path, conf_threshold],
                    outputs=save_output
                )
            
            with gr.Tab("Object Detection"):
                with gr.Row():
                    with gr.Column():
                        start_btn = gr.Button("Start")
                        stop_btn = gr.Button("Stop")
                        conf_slider = gr.Slider(
                            minimum=0.1,
                            maximum=1.0,
                            value=self.config["conf_threshold"],
                            label="Confidence Threshold"
                        )
                        threshold_status = gr.Textbox(label="Threshold Status")
                    with gr.Column():
                        video_output = gr.Image(
                            label="Camera Feed",
                            type="numpy"
                        )
                        detection_output = gr.Textbox(label="Detections")
                
                def continuous_update():
                    try:
                        # Show first frame immediately
                        frame, text = self.start_detection()
                        if frame is not None:
                            yield frame, text
                        
                        # Continuous updates
                        while self.is_running:
                            frame, text = self.process_frame()
                            if frame is not None:
                                yield frame, text
                            else:
                                print(f"No frame available: {text}")
                                break
                            time.sleep(0.1)
                    except Exception as e:
                        print(f"Error in continuous_update: {str(e)}")
                        yield None, f"Error: {str(e)}"
                
                start_btn.click(
                    fn=continuous_update,
                    outputs=[video_output, detection_output]
                )
                
                stop_btn.click(
                    fn=self.stop_detection,
                    outputs=[threshold_status]
                )
                
                conf_slider.change(
                    fn=self.update_threshold,
                    inputs=[conf_slider],
                    outputs=[threshold_status]
                )
            
            return ui

def main():
    app = DetectionApp()
    ui = app.create_ui()
    ui.launch(server_name="0.0.0.0", server_port=7860)

if __name__ == "__main__":
    main()
