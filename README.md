# Raspberry Pi Object Detection with MQTT

A real-time object detection application for Raspberry Pi using YOLOv8 and MQTT, built with Gradio for an interactive web interface.

## Features

- Real-time object detection using Raspberry Pi Camera
- YOLO v8 neural network for accurate object detection
- MQTT integration for IoT connectivity
- Web-based user interface using Gradio
- Adjustable confidence threshold during runtime
- Live video feed with detection visualization
- Multi-tab interface for settings and detection

## Requirements

### Hardware
- Raspberry Pi (tested on Raspberry Pi 4)
- Raspberry Pi Camera Module
- Internet connection for MQTT (if using remote broker)

### Software
- Raspberry Pi OS (Bullseye or newer)
- Python 3.9+
- MQTT Broker (e.g., Mosquitto)
- Required Python packages (installed automatically)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/phillipfoxsmaflex/object_detection_rpi
cd raspberry-detection
```

2. Run the installation script:
```bash
sudo ./install.sh
```

The installation script will:
- Install required system packages
- Set up Python virtual environment
- Install Python dependencies
- Download YOLOv8 model
- Configure MQTT broker
- Set up camera permissions
- Create necessary directories and configuration files
- Set up systemd service (optional)

## Configuration

### MQTT Settings
Edit `config/settings.json` to configure MQTT connection:
```json
{
    "mqtt_broker": "localhost",
    "mqtt_port": 1883,
    "mqtt_topic": "detections",
    "model_path": "models/yolov8n.pt",
    "conf_threshold": 0.25
}
```

### Camera Settings
The camera is configured to use a resolution of 640x480 by default. You can modify this in `src/camera.py`.

### Model Settings
- Default model: YOLOv8n (nano version)
- Location: `models/yolov8n.pt`
- You can replace it with other YOLOv8 models for different performance/accuracy trade-offs

## Usage

### Starting the Application

1. Normal start:
```bash
./start.sh
```

2. Debug mode (with logging):
```bash
./start_debug.sh
```

3. Camera test:
```bash
./test_camera.sh
```

4. As a system service:
```bash
sudo systemctl start object-detection
```

### Accessing the Web Interface

1. Open a web browser and navigate to:
```
http://[raspberry-pi-ip]:7860
```

2. The interface has two tabs:
   - Settings: Configure MQTT and model parameters
   - Object Detection: Live detection with adjustable confidence threshold

### Using the Object Detection Tab

1. Click "Start" to begin object detection
2. Adjust confidence threshold using the slider
3. View detections in real-time
4. Click "Stop" to end detection

### MQTT Messages

Detection results are published to the configured MQTT topic in JSON format:
```json
{
    "person": {
        "count": 2,
        "confidences": [0.92, 0.87]
    },
    "car": {
        "count": 1,
        "confidences": [0.95]
    }
}
```

## Troubleshooting

### Camera Issues
1. Check camera connection
2. Verify camera is enabled:
```bash
vcgencmd get_camera
```
3. Check permissions:
```bash
ls -l /dev/video*
```

### MQTT Issues
1. Check MQTT broker status:
```bash
sudo systemctl status mosquitto
```
2. Test MQTT connection:
```bash
mosquitto_sub -t "detections"
```

### Log Files
- Check application logs:
```bash
tail -f logs/debug.log
```
- Check system logs:
```bash
sudo journalctl -u object-detection
```

## Development

### Project Structure
```
raspberry-detection/
├── config/
│   └── settings.json
├── models/
│   └── yolov8n.pt
├── src/
│   ├── app.py
│   ├── camera.py
│   ├── mqtt_client.py
│   └── object_detection.py
├── logs/
├── requirements.txt
└── README.md
```

### Main Components
- `app.py`: Main application with Gradio interface
- `camera.py`: Camera handling using picamera2
- `mqtt_client.py`: MQTT client implementation
- `object_detection.py`: YOLOv8 object detection

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- YOLOv8 by Ultralytics
- Gradio team for the web interface framework
- Raspberry Pi Foundation
- Eclipse Mosquitto project
