from flask import Flask, render_template
from flask_socketio import SocketIO
import paho.mqtt.client as mqtt
import threading

app = Flask(__name__)
socketio = SocketIO(app)

MQTT_BROKER_ADDRESS = "localhost"
MQTT_PORT = 1883

# Global variable to store MQTT messages
messages = []

# MQTT setup
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe("your/topic")  # Subscribe to your MQTT topic

def on_message(client, userdata, msg):
    print(msg)
    global messages
    messages.append(str(msg.payload.decode("utf-8")))
    messages = messages[-10:]  # Keep the last 10 messages
    socketio.emit('mqtt_update', {'message': messages})

mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect(MQTT_BROKER_ADDRESS, MQTT_PORT, 60)

# Start the MQTT client in a separate thread
threading.Thread(target=mqtt_client.loop_forever).start()

@app.route('/')
def index():
    return render_template('index.html', messages=messages)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)