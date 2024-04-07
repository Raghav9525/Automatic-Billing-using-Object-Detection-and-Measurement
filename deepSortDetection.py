import math
import cv2
import numpy as np
from ultralytics import YOLO
import cvzone
from utils import config
from sort import Sort

def deep_sort_detection():
    classNames = config.classNames

    # list of items to detect
    shop_item = ['apple', 'banana']

    detector = YOLO('./YOLOweights/yolov8l.pt')
    cap = cv2.VideoCapture(0)

    # Set resolution
    cap.set(3, 1280)
    cap.set(4, 720)

    # initialize tracker
    tracker = Sort(max_age=20, min_hits=3, iou_threshold=0.3)

    while True:
        ret, frame = cap.read()
        outputs = detector(frame, stream=True)

        # empty array declaration to store coordinates and id
        detections = np.empty((0, 5))

        item_detected = False  # Flag to indicate if the item is detected

        for output in outputs:
            boxes = output.boxes
            print(boxes)
            for box in boxes:
                # // get coordinates of bounding box
                x1, y1, x2, y2 = box.xyxy[0]
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                w, h = x2 - x1, y2 - y1

                # get confidence
                conf = math.ceil((box.conf[0] * 100)) / 100

                # create rectangle
                cvzone.cornerRect(frame, (x1, y1, w, h))

                # display class name
                cls = int(box.cls[0])
                cvzone.putTextRect(frame, f'{classNames[cls]}', (max(0, x1), max(35, y1)))

                currentArray = np.array([x1, y1, x2, y2, conf])
                detections = np.vstack((detections, currentArray))

        # update detection via tracker
        resultTracker = tracker.update(detections)

        for result in resultTracker:
            x1, y1, x2, y2, id = result
            print(result)

        # if item_detected:
        #     break  # Breaks out of the outer loop if an item is detected

        cv2.imshow('win', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the capture and close windows
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    deep_sort_detection()
