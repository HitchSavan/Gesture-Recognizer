import mediapipe as mp
from mediapipe.tasks import python
from mediapipe import solutions
from mediapipe.framework.formats import landmark_pb2
import numpy as np
import os
import cv2
from time import time

def draw_landmarks_on_image(rgb_image, detection_result, MARGIN, FONT_SIZE, HANDEDNESS_TEXT_COLOR, FONT_THICKNESS):
    hand_landmarks_list = detection_result.hand_landmarks
    handedness_list = detection_result.handedness
    annotated_image = np.copy(rgb_image)

    # Loop through the detected hands to visualize.
    for idx in range(len(hand_landmarks_list)):
        hand_landmarks = hand_landmarks_list[idx]
        handedness = handedness_list[idx]

        # Draw the hand landmarks.
        hand_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
        hand_landmarks_proto.landmark.extend([
            landmark_pb2.NormalizedLandmark(x=landmark.x, y=landmark.y, z=landmark.z) for landmark in hand_landmarks
        ])
        solutions.drawing_utils.draw_landmarks(
            annotated_image,
            hand_landmarks_proto,
            solutions.hands.HAND_CONNECTIONS,
            solutions.drawing_styles.get_default_hand_landmarks_style(),
            solutions.drawing_styles.get_default_hand_connections_style())

        # Get the top left corner of the detected hand's bounding box.
        height, width, _ = annotated_image.shape
        x_coordinates = [landmark.x for landmark in hand_landmarks]
        y_coordinates = [landmark.y for landmark in hand_landmarks]
        text_x = int(min(x_coordinates) * width)
        text_y = int(min(y_coordinates) * height) - MARGIN

        # Draw handedness (left or right hand) on the image.
        cv2.putText(annotated_image, f"{handedness[0].category_name}",
                    (text_x, text_y), cv2.FONT_HERSHEY_DUPLEX,
                    FONT_SIZE, HANDEDNESS_TEXT_COLOR, FONT_THICKNESS, cv2.LINE_AA)

    return annotated_image

def gesture_detection_init(path):
    print("Loading gesture detection model...")
    try:
        model_path = f'{path}/gesture_tracker/hand_landmarker.task'
    except:
        model_path = f'{path}\\gesture_tracker\\hand_landmarker.task'


    MARGIN = 10  # pixels
    FONT_SIZE = 1
    FONT_THICKNESS = 1
    HANDEDNESS_TEXT_COLOR = (0, 255, 255) # RGB
    gest_format = (MARGIN, FONT_SIZE, HANDEDNESS_TEXT_COLOR, FONT_THICKNESS)

    with open(model_path, 'rb') as f:
        model = f.read()

    HandLandmarkerResult = mp.tasks.vision.HandLandmarkerResult
    BaseOptions = python.BaseOptions(model_asset_buffer=model)
    HandLandmarker = mp.tasks.vision.HandLandmarker
    HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
    VisionRunningMode = mp.tasks.vision.RunningMode

    # Create a hand landmarker instance with the live stream mode:
    def print_result(result: HandLandmarkerResult, output_image: mp.Image, timestamp_ms: int):
        
        annotated_frame = draw_landmarks_on_image(output_image.numpy_view(), result, *gest_format)
        
        # Display the resulting frame
        cv2.imshow('frame', annotated_frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            return 0    

    options = HandLandmarkerOptions(
        base_options=BaseOptions,
        num_hands=2,
        running_mode=VisionRunningMode.LIVE_STREAM,
        result_callback=print_result)
        
    return (HandLandmarker, options)

def detect_gesture(landmarker, frame):
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
    timestamp = int(time() * 1000)
    
    landmarker.detect_async(mp_image, timestamp)


if __name__ == '__main__':

    path = os.getcwd()

    print('Opening camera...')
    vid = cv2.VideoCapture(0)

    HandLandmarker, options = gesture_detection_init(path)

    with HandLandmarker.create_from_options(options) as landmarker:
        while(True):
            # Capture the video frame by frame
            ret, frame = vid.read()

            detect_gesture(landmarker, frame)
            
            # the 'q' button is quitting button
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # After the loop release the cap object
        vid.release()
        # Destroy all the windows
        cv2.destroyAllWindows()