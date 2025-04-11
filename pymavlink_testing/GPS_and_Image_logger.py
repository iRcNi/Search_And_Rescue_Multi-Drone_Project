# gps_image_logger.py
# Captures camera frames and names them with GPS coordinates

from pymavlink import mavutil
import time
import cv2
import os

# Connect to the drone (SiK Radio)
connection_string = '/dev/ttyUSB0'  # Update if needed
baud_rate = 57600

print(f"Connecting to {connection_string} at {baud_rate}...")
master = mavutil.mavlink_connection(connection_string, baud=baud_rate)

print("Waiting for heartbeat...")
master.wait_heartbeat()
print(f"Connected to system {master.target_system}, component {master.target_component}")

# Request GPS data at 1Hz
master.mav.request_data_stream_send(
    master.target_system,
    master.target_component,
    mavutil.mavlink.MAV_DATA_STREAM_POSITION,
    1,
    1
)

# Open the USB camera (usually index 0 or 1)
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Cannot open USB camera.")
    exit()

# Make output folder
os.makedirs("frames", exist_ok=True)

while True:
    # Get GPS data
    msg = master.recv_match(type='GPS_RAW_INT', blocking=True, timeout=5)

    if msg is not None and msg.fix_type >= 2:
        lat = msg.lat / 1e7
        lon = msg.lon / 1e7
        alt = msg.alt / 1000.0

        # Capture frame
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture image from camera.")
            continue

        # Format filename using GPS coords
        filename = f"frames/{lat:.7f}_{lon:.7f}_{alt:.2f}.jpg"
        filename = filename.replace(" ", "_")  # just in case

        # Save frame
        cv2.imwrite(filename, frame)
        print(f"Saved frame: {filename}")

    else:
        print("No GPS fix or data timeout...")

    time.sleep(2)
