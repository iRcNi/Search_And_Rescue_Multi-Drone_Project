# gps_yolo_logger_with_boxes.py
# Detects person using YOLOv8, draws bounding boxes, and saves the frame with GPS coords as filename

from pymavlink import mavutil
import time
import cv2
import os
from ultralytics import YOLO

# Initialize YOLOv8 model
model = YOLO("yolov8x.pt")  # You can change to yolov8s.pt, etc.

# Connect to drone via SiK radio
connection_string = '/dev/ttyUSB0'
baud_rate = 57600

print(f"Connecting to {connection_string} at {baud_rate}...")
master = mavutil.mavlink_connection(connection_string, baud=baud_rate)

print("Waiting for heartbeat...")
master.wait_heartbeat()
print(f"Connected to system {master.target_system}, component {master.target_component}")

# Request GPS data stream
master.mav.request_data_stream_send(
    master.target_system,
    master.target_component,
    mavutil.mavlink.MAV_DATA_STREAM_POSITION,
    1,
    1
)

# Initialize camera
cap = cv2.VideoCapture(1)
if not cap.isOpened():
    print("Error: Cannot open camera.")
    exit()

# Output folder
os.makedirs("detections", exist_ok=True)

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to read from camera.")
        continue

    # Run YOLOv8 inference
    results = model(frame)

    for result in results:
        # Only proceed if person is detected
        if result.boxes is not None:
            boxes = result.boxes.xyxy.cpu().numpy()     # [x1, y1, x2, y2]
            classes = result.boxes.cls.cpu().numpy()    # class IDs

            found_person = False

            for i, class_id in enumerate(classes):
                if int(class_id) == 0:  # Class 0 = person
                    found_person = True

                    # Draw the bounding box
                    x1, y1, x2, y2 = boxes[i].astype(int)
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(frame, "Person", (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            if found_person:
                # Get GPS
                msg = master.recv_match(type='GPS_RAW_INT', blocking=True, timeout=5)
                if msg is not None and msg.fix_type >= 2:
                    lat = msg.lat / 1e7
                    lon = msg.lon / 1e7
                    alt = msg.alt / 1000.0

                    # Save image with coords as filename
                    filename = f"detections/{lat:.7f}_{lon:.7f}_{alt:.2f}.jpg"
                    filename = filename.replace(" ", "_")
                    cv2.imwrite(filename, frame)
                    print(f"Person detected! Saved with box: {filename}")
                else:
                    print("Person detected, but no GPS fix yet.")

            break  # Save only once per frame
