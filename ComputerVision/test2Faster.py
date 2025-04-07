from ultralytics import YOLO
import cv2

# Flag to indicate human detection
human_detected = False

# Load YOLOv8 model
model = YOLO("yolov8n.pt")

# Open the external camera
cap = cv2.VideoCapture("http://192.168.1.6:4747/video")

if not cap.isOpened():
    print("Error: Could not open camera.")
    exit()

fps = int(cap.get(cv2.CAP_PROP_FPS))
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

out = cv2.VideoWriter("output_video.mp4", cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height))

while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: Failed to read frame.")
        break

    human_detected = False  # Reset flag for this frame

    results = model(frame)

    for r in results:
        for box in r.boxes:
            class_id = int(box.cls[0])
            label = model.names[class_id]

            if label == "person":
                human_detected = True  # Set the flag if person detected

                x1, y1, x2, y2 = map(int, box.xyxy[0])
                confidence = box.conf[0].item()

                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, f"{label} {confidence:.2f}", (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # ✅ Print flag status to console
    print("Human Detected:", human_detected)

    cv2.imshow("Real-Time YOLO Detection", frame)
    out.write(frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
out.release()
cv2.destroyAllWindows()