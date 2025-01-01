import paho.mqtt.client as mqtt
import json

class MQTTClient:
    def __init__(self, broker, port, topic):
        self.client = mqtt.Client()
        self.broker = broker
        self.port = port
        self.topic = topic
        
    def connect(self):
        self.client.connect(self.broker, self.port)
        self.client.loop_start()
        
    def publish_detections(self, detections):
        message = json.dumps(detections)
        self.client.publish(self.topic, message)
        
    def disconnect(self):
        self.client.loop_stop()
        self.client.disconnect()