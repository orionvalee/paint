import cv2
import mediapipe as mp
import tkinter as tk
from tkinter import Canvas, Frame, Button, Label
import numpy as np

# Global variables
drawing_color = "red"  # Default drawing color
brush_size = 5
drawing = False
last_x, last_y = None, None

# MediaPipe setup
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils

def get_landmark_coordinates(landmarks, landmark_id, frame_width, frame_height):
    """Converts normalized landmark coordinates to pixel coordinates."""
    landmark = landmarks.landmark[landmark_id]
    return int(landmark.x * frame_width), int(landmark.y * frame_height)

def is_finger_up(landmarks, finger_tip_id, finger_pip_id, finger_mcp_id=None):
    """Checks if a finger is extended."""
    tip = landmarks.landmark[finger_tip_id]
    pip = landmarks.landmark[finger_pip_id]

    # For thumb, we check x-coordinate relative to MCP if hand is vertical,
    # or y-coordinate if hand is horizontal (less reliable, simple check here)
    if finger_tip_id == mp_hands.HandLandmark.THUMB_TIP:
         mcp = landmarks.landmark[mp_hands.HandLandmark.THUMB_MCP]
         # Simplified: Check if thumb tip is further out than PIP from MCP (assuming right hand for x)
         # A more robust solution would consider hand orientation
         return tip.x < pip.x if abs(tip.x - mcp.x) > abs(tip.y - mcp.y) else tip.y < pip.y


    # For other fingers, check if tip is above PIP
    return tip.y < pip.y

def is_drawing_gesture(landmarks):
    """Index finger up, others down."""
    index_up = is_finger_up(landmarks, mp_hands.HandLandmark.INDEX_FINGER_TIP, mp_hands.HandLandmark.INDEX_FINGER_PIP)
    middle_down = not is_finger_up(landmarks, mp_hands.HandLandmark.MIDDLE_FINGER_TIP, mp_hands.HandLandmark.MIDDLE_FINGER_PIP)
    ring_down = not is_finger_up(landmarks, mp_hands.HandLandmark.RING_FINGER_TIP, mp_hands.HandLandmark.RING_FINGER_PIP)
    pinky_down = not is_finger_up(landmarks, mp_hands.HandLandmark.PINKY_TIP, mp_hands.HandLandmark.PINKY_PIP)
    return index_up and middle_down and ring_down and pinky_down

def get_selected_color_gesture(landmarks):
    """
    Determines color based on finger gestures.
    - Index and Middle finger tips touching: Red
    - Index and Thumb tips touching: Blue
    - All fingers closed (fist): Green (simple example)
    - Index and Pinky up: Eraser (white)
    """
    global drawing_color

    index_tip = landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
    middle_tip = landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
    thumb_tip = landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
    pinky_tip = landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP]

    # Helper to check if two landmarks are close
    def are_landmarks_close(lm1, lm2, threshold=0.05): # Threshold is normalized
        return ((lm1.x - lm2.x)**2 + (lm1.y - lm2.y)**2)**0.5 < threshold

    # Index and Middle for Red
    if are_landmarks_close(index_tip, middle_tip):
        return "red"

    # Index and Thumb for Blue
    if are_landmarks_close(index_tip, thumb_tip):
        return "blue"

    # Index and Pinky up for Eraser
    index_up = is_finger_up(landmarks, mp_hands.HandLandmark.INDEX_FINGER_TIP, mp_hands.HandLandmark.INDEX_FINGER_PIP)
    pinky_up = is_finger_up(landmarks, mp_hands.HandLandmark.PINKY_TIP, mp_hands.HandLandmark.PINKY_PIP)
    middle_down = not is_finger_up(landmarks, mp_hands.HandLandmark.MIDDLE_FINGER_TIP, mp_hands.HandLandmark.MIDDLE_FINGER_PIP)
    ring_down = not is_finger_up(landmarks, mp_hands.HandLandmark.RING_FINGER_TIP, mp_hands.HandLandmark.RING_FINGER_PIP)

    if index_up and pinky_up and middle_down and ring_down:
        return "white" # Eraser

    # All fingers closed (fist) for Green (simplified)
    # Check if all fingertips are below their respective PIP joints
    all_closed = True
    for finger_tip_id, finger_pip_id in [
        (mp_hands.HandLandmark.INDEX_FINGER_TIP, mp_hands.HandLandmark.INDEX_FINGER_PIP),
        (mp_hands.HandLandmark.MIDDLE_FINGER_TIP, mp_hands.HandLandmark.MIDDLE_FINGER_PIP),
        (mp_hands.HandLandmark.RING_FINGER_TIP, mp_hands.HandLandmark.RING_FINGER_PIP),
        (mp_hands.HandLandmark.PINKY_TIP, mp_hands.HandLandmark.PINKY_PIP),
    ]:
        if is_finger_up(landmarks, finger_tip_id, finger_pip_id):
            all_closed = False
            break
    if all_closed and not is_finger_up(landmarks, mp_hands.HandLandmark.THUMB_TIP, mp_hands.HandLandmark.THUMB_IP): # Thumb also curled
        return "green"

    return None


def update_drawing(event):
    """Handles drawing on the canvas when mouse is dragged (for testing)."""
    global last_x, last_y, drawing_color, brush_size
    x, y = event.x, event.y
    if last_x and last_y:
        canvas.create_line(last_x, last_y, x, y, fill=drawing_color, width=brush_size, capstyle=tk.ROUND, smooth=tk.TRUE)
    last_x, last_y = x, y

def start_draw_mouse(event):
    global last_x, last_y
    last_x, last_y = event.x, event.y

def stop_draw_mouse(event):
    global last_x, last_y
    last_x, last_y = None, None

def main_loop():
    global drawing_color, brush_size, drawing, last_x, last_y

    ret, frame = cap.read()
    if not ret:
        root.after(10, main_loop)
        return

    frame = cv2.flip(frame, 1)
    frame_height, frame_width, _ = frame.shape
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    # Create a combined image: camera feed on left, drawing canvas on right
    # For simplicity, we'll draw directly on a Tkinter canvas and show camera separately for now.
    # A more integrated view would require putting CV frame onto a Tkinter canvas.

    current_gesture_color = None
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            # Draw landmarks on the frame (optional, for debugging)
            # mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Color selection
            new_color = get_selected_color_gesture(hand_landmarks)
            if new_color:
                drawing_color = new_color
                color_status_label.config(text=f"Color: {drawing_color.upper()}", fg=drawing_color if drawing_color != "white" else "black")

            # Drawing gesture
            if is_drawing_gesture(hand_landmarks):
                ix, iy = get_landmark_coordinates(hand_landmarks, mp_hands.HandLandmark.INDEX_FINGER_TIP, frame_width, frame_height)

                # Convert camera coordinates to canvas coordinates
                # This needs calibration if camera view and canvas view are different aspect ratios/sizes
                # Assuming canvas fills a portion of the screen, and camera feed is separate.
                # For direct mapping, ensure canvas size matches camera feed aspect ratio.
                canvas_x = int(ix * (canvas.winfo_width() / frame_width))
                canvas_y = int(iy * (canvas.winfo_height() / frame_height))

                if last_x is None or last_y is None : # Started drawing
                    last_x, last_y = canvas_x, canvas_y

                current_brush_size = 15 if drawing_color == "white" else brush_size # Eraser size
                canvas.create_line(last_x, last_y, canvas_x, canvas_y, fill=drawing_color, width=current_brush_size, capstyle=tk.ROUND, smooth=tk.TRUE)
                last_x, last_y = canvas_x, canvas_y
                drawing = True
            else:
                last_x, last_y = None, None # Stop drawing if gesture changes
                drawing = False
    else: # No hands detected
        last_x, last_y = None, None
        drawing = False


    # Display the camera feed (optional, can be a separate window or integrated)
    cv2.imshow('Camera Feed', frame)

    root.after(10, main_loop) # Schedule the next frame processing

# --- Tkinter GUI Setup ---
root = tk.Tk()
root.title("Air Painter")

# Canvas for drawing
canvas_width = 800
canvas_height = 600
canvas = Canvas(root, width=canvas_width, height=canvas_height, bg="white", cursor="cross")
canvas.pack(pady=20, expand=tk.YES, fill=tk.BOTH)

# Mouse drawing bindings (for testing GUI without camera)
# canvas.bind("<B1-Motion>", update_drawing)
# canvas.bind("<ButtonPress-1>", start_draw_mouse)
# canvas.bind("<ButtonRelease-1>", stop_draw_mouse)

# Color selection buttons (alternative/debug)
controls_frame = Frame(root)
controls_frame.pack(pady=10)

def set_color(new_color):
    global drawing_color
    drawing_color = new_color
    color_status_label.config(text=f"Color: {drawing_color.upper()}", fg=drawing_color if drawing_color != "white" else "black")


Button(controls_frame, text="Red", bg="red", command=lambda: set_color("red")).pack(side=tk.LEFT, padx=5)
Button(controls_frame, text="Blue", bg="blue", command=lambda: set_color("blue")).pack(side=tk.LEFT, padx=5)
Button(controls_frame, text="Green", bg="green", command=lambda: set_color("green")).pack(side=tk.LEFT, padx=5)
Button(controls_frame, text="Eraser", bg="white", command=lambda: set_color("white")).pack(side=tk.LEFT, padx=5)

color_status_label = Label(controls_frame, text=f"Color: {drawing_color.upper()}", font=("Arial", 14), fg=drawing_color)
color_status_label.pack(side=tk.LEFT, padx=20)


# OpenCV Camera Setup
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Cannot open camera")
    exit()

# Start the main loop
main_loop()
root.mainloop()

# Cleanup
cap.release()
cv2.destroyAllWindows()
hands.close()

print("Application closed.")
