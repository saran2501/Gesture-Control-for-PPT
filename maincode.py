import mediapipe as mp
import cv2
import pyautogui

mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands
buttonpress = False
counter = 0
delay = 30

cap = cv2.VideoCapture(0)
cap.set(3, 1920)
cap.set(4, 1080)

with mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5) as hands:
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)

        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False

        results = hands.process(image)

        image.flags.writeable = True
        cropped_frame = None

        if results.multi_hand_landmarks and buttonpress is False:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                landmarks = hand_landmarks.landmark

                # Calculate bounding box
                x_coords = [int(lm.x * frame.shape[1]) for lm in landmarks]
                y_coords = [int(lm.y * frame.shape[0]) for lm in landmarks]
                x_min, x_max = min(x_coords), max(x_coords)
                y_min, y_max = min(y_coords), max(y_coords)

                # Add padding to bounding box
                padding = 20
                x_min = max(0, x_min - padding)
                y_min = max(0, y_min - padding)
                x_max = min(frame.shape[1], x_max + padding)
                y_max = min(frame.shape[0], y_max + padding)

                # Draw bounding box on original frame
                cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)

                # Crop the region of interest (ROI)
                 #cropped_frame = frame[y_min:y_max, x_min:x_max]

                # Logic for finger up detection
                finger_tips = [8, 12, 16, 20]  # Tips
                finger_joints = [6, 10, 14, 18]  # Joints

                finger_up = []
                for tip, joint in zip(finger_tips, finger_joints):
                    if landmarks[tip].y < landmarks[joint].y:  # finger up
                        finger_up.append(1)
                    else:
                        finger_up.append(0)

                if landmarks[4].x > landmarks[3].x:  # Thumb extended
                    finger_up.append(1)
                else:
                    finger_up.append(0)

                print("Fingers Up:", finger_up)

                # Swipe right
                if finger_up == [0, 0, 0, 0, 1]:
                    print("Right swipe detected")
                    buttonpress = True
                    pyautogui.press("right")

                # Swipe left
                if finger_up == [1, 1, 0, 0, 0]:
                    print("Left swipe detected")
                    buttonpress = True
                    pyautogui.press("left")

                if finger_up == [1, 1, 1, 0, 0]:
                    print("Exiting presentation mode")
                    buttonpress = True
                    # pyautogui.hotkey("alt", "f4")

        if buttonpress:
            counter += 1
            if counter > delay:
                counter = 0
                buttonpress = False

        ''' Display the cropped frame
        if cropped_frame is not None:
            cv2.imshow('Cropped Hand', cropped_frame)

        # Display the full frame with bounding box for debugging
        cv2.imshow('Hand Tracking', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break'''

cap.release()
cv2.destroyAllWindows()
