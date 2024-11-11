import psutil
from flask_socketio import SocketIO
import time

# Function to get battery status
def get_battery_status():
    battery = psutil.sensors_battery()
    if battery:
        return battery.percent
    else:
        return None

def send_battery_status(socketio):
    """Background function to send battery status to the frontend."""
    while True:
        battery_status = get_battery_status()
        if battery_status is not None:
            # Emit battery status to the frontend every 30 seconds
            socketio.emit('battery_status', {'status': f'Battery: {battery_status}%'})
        else:
            # If battery information is unavailable, send a default message
            socketio.emit('battery_status', {'status': 'Battery status unavailable'})
        
        time.sleep(30)  # Update every 30 seconds
