import sys
import os

path = os.getcwd()
sys.path.insert(0, f'{path}\\hand_detector')
sys.path.insert(0, f'{path}\\gesture_tracker')

from hand_detector.yolo_detect import *
from gesture_tracker.GestureTrackingModule_Image import *

path = os.getcwd()

prev_timestamp = time()

print('Opening camera...')
vid = cv2.VideoCapture(0)

model, *yolo_format = yolo_init(path)
HandLandmarker, options, gest_format = gesture_detection_init(path)

with HandLandmarker.create_from_options(options) as landmarker:
    while(True):
        # Capture the video frame by frame
        ret, frame = vid.read()

        frame, prev_timestamp, crop_coords = yolo(model, yolo_format, frame, prev_timestamp)
        
        if crop_coords:
            for box in crop_coords:
                annotated_image = frame
                annotated_image = np.array(frame[box[1]:box[3], box[0]:box[2]])
                annotated_image, prev_timestamp = detect_gesture(landmarker, gest_format, annotated_image, prev_timestamp)
                cv2.imshow('frame', annotated_image)
        else:
            annotated_image, prev_timestamp = detect_gesture(landmarker, gest_format, frame, prev_timestamp)
            cv2.imshow('frame', annotated_image)

        # the 'q' button is quitting button
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # After the loop release the cap object
    vid.release()
    # Destroy all the windows
    cv2.destroyAllWindows()