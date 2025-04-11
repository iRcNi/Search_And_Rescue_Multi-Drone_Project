from ultralytics import YOLO
from pymavlink import mavutil
import cv2
import time

print("[MAVLink] Connecting to drone...")
master = mavutil.mavlink_connection('udp:127.0.0.1:14550')
master.wait_heartbeat()
print("[MAVLink] Heartbeat received.")

def set_flight_mode(mode):
    mode_id = master.mode_mapping().get(mode)
    if mode_id is None:
        print(f"[MAVLink] Flight mode {mode} not recognized!")
        return
    master.mav.set_mode_send(
        master.target_system,
        mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
        mode_id
    )
    print(f"[MAVLink] Flight mode changed to {mode}")

# Set AUTO mode at the beginning
set_flight_mode('AUTO')
time.sleep(1)

print("[MAVLink] Arming...")
master.mav.command_long_send(
    master.target_system, master.target_component,
    mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
    0, 1, 0, 0, 0, 0, 0, 0
)

print("[MAVLink] Taking off to 100m...")
master.mav.command_long_send(
    master.target_system, master.target_component,
    mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,
    0, 0, 0, 0, 0, 0, 0, 100
)

time.sleep(10)  # Wait for takeoff

print("Mission started... will save frames if a person is detected.")

model = YOLO("yolov8n.pt")
cap = cv2.VideoCapture(1)  # your IP stream

if not cap.isOpened():
    print("Error: Could not open camera.")
    exit()

fps = int(cap.get(cv2.CAP_PROP_FPS) or 30)
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 640)
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 480)

out = cv2.VideoWriter("output_video.mp4", cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height))

frame_count = 0
saved_frame_index = 0

while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: Failed to read frame.")
        break

    results = model(frame)
    human_detected = False

    for r in results:
        for box in r.boxes:
            class_id = int(box.cls[0])
            label = model.names[class_id]

            if label == "person":
                human_detected = True
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                confidence = box.conf[0].item()

                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, f"{label} {confidence:.2f}", (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                # Save frame if a person is detected
                filename = f"person_frame_{saved_frame_index:04}.jpg"
                cv2.imwrite(filename, frame)
                print(f"[📸] Saved frame: {filename}")
                saved_frame_index += 1

    print("Human Detected:", human_detected)

    cv2.imshow("Real-Time YOLO Detection", frame)
    out.write(frame)
    frame_count += 1

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
out.release()
cv2.destroyAllWindows()
