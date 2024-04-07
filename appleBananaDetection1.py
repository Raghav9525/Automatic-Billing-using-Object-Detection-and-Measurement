import threading
import cv2
from ultralytics import YOLO
import cvzone
from utils import config  # Assuming a "utils" module with config
import math
import serial

# Initialize serial port configuration for weight measurement
serial_port = 'COM4'  # Change to your Arduino's serial port
baud_rate = 57600
weight = "0"

def read_serial(stop_event, ser):
    global weight
    while not stop_event.is_set():
        if ser.in_waiting > 0:
            weight = ser.readline().decode().strip()
            print(weight)

def detections(response_dict, stop_detection_flag):
    # Initialize serial port inside the function to ensure proper closure
    ser = serial.Serial(serial_port, baud_rate)
    stop_thread = threading.Event()

    # Start the serial reading in a separate thread
    serial_thread = threading.Thread(target=read_serial, args=(stop_thread, ser))
    serial_thread.start()

    # Assuming classNames and detector initialization
    classNames = config.classNames
    detector = YOLO('./YOLOweights/yolov8l.pt')

    # Camera setup
    cap = cv2.VideoCapture(0)
    cap.set(3, 1280)
    cap.set(4, 720)

    # Initialize counts
    frame_ids = {
        "bananaCount": [],
        "appleCount": [],
        "carrotCount": [],
        "broccoliCount":[]
    }
    objectName = ""

    try:
        while True:
            # Check if the stop signal is set
            if stop_detection_flag.is_set():
                break
            
            ret, frame = cap.read()
            if not ret:
                print("Error capturing frame")
                break

            outputs = detector(frame, stream=True)
            currentObjectName = ""
            for output in outputs:    
                boxes = output.boxes
                for box in boxes:
                    className = classNames[int(box.cls[0])]

                    if className in ["banana", "apple",'carrot','broccoli']:
                        x1, y1, x2, y2 = map(int, box.xyxy[0])
                        conf = math.ceil((box.conf[0] * 100)) / 100
                        cvzone.cornerRect(frame, (x1, y1, x2 - x1, y2 - y1), l=9, rt=2, colorR=(255, 0, 0))
                        cvzone.putTextRect(frame, f'{className} {conf}', (x1, y1 - 10), scale=1, thickness=2, offset=0)
                        currentObjectName = className

            if currentObjectName:
                objectName = currentObjectName

            if objectName and weight:  # Ensure weight is not empty
                frame_ids[objectName + "Count"].append(weight)

            cv2.imshow('Video', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except KeyboardInterrupt:
        print("\nInterrupted by user, closing...")
    except Exception as e:
        print(f"Error in detection thread: {e}")
    finally:
        stop_thread.set()
        serial_thread.join()

        ser.close()
        cap.release()
        cv2.destroyAllWindows()
        
        for item, counts in frame_ids.items():
            # Convert weights to float for comparison, assuming they are numeric
            counts = [float(i) for i in counts]
            response_dict[item] = str(max(counts)) if counts else "0"

        print(response_dict)


