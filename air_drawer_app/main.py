import cv2
import mediapipe as mp
import tkinter as tk
from tkinter import Canvas, Frame, Button, Label
import numpy as np

# Global variables
drawing_color = "red"  # Default drawing color
brush_size = 5
# drawing = False # Not strictly needed as a global, managed by last_x, last_y
last_x, last_y = None, None

# MediaPipe setup
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils

def get_landmark_coordinates(landmarks, landmark_id, frame_width, frame_height):
    """Converts normalized landmark coordinates to pixel coordinates."""
    landmark = landmarks.landmark[landmark_id]
    return int(landmark.x * frame_width), int(landmark.y * frame_height)

def is_finger_up(landmarks, finger_tip_id, finger_pip_id, finger_dip_id=None, finger_mcp_id=None):
    """
    Checks if a finger is extended.
    For thumb, checks if tip is further from wrist than IP joint.
    For other fingers, checks if tip is "above" (smaller y) PIP joint.
    A more robust check might compare angles or distances to palm center.
    """
    tip = landmarks.landmark[finger_tip_id]
    pip = landmarks.landmark[finger_pip_id]

    if finger_tip_id == mp_hands.HandLandmark.THUMB_TIP:
        ip = landmarks.landmark[mp_hands.HandLandmark.THUMB_IP]
        mcp = landmarks.landmark[mp_hands.HandLandmark.THUMB_MCP] # MCP is closer to wrist
        # Thumb is up if tip is further from MCP than IP joint (on y-axis primarily for vertical hand)
        # and also further out than the MCP joint itself.
        # This is a heuristic and can be improved.
        # Check relative distance: tip further from mcp than pip is from mcp.
        # A simple check: is tip.y < ip.y (if hand upright) or tip.x < ip.x (if hand sideways for right hand)
        # Let's use a slightly more general approach for thumb:
        # If the hand is mostly vertical, y difference is dominant. If horizontal, x difference.
        # Compare tip to pip (or ip for thumb)
        # For thumb, it's "up" if it's extended away from the palm.
        # A simple check: if tip.y < pip.y and tip.y < landmarks.landmark[mp_hands.HandLandmark.THUMB_MCP].y
        # Or, more simply, if the tip is higher than the IP joint.
        return tip.y < ip.y and tip.x < mcp.x # Assuming right hand, thumb to the left and up when extended
    else:
        # For other fingers, check if tip is above PIP (smaller y-coordinate)
        # and for more certainty, also above DIP if available
        if finger_dip_id:
            dip = landmarks.landmark[finger_dip_id]
            return tip.y < pip.y and tip.y < dip.y
        return tip.y < pip.y


def is_drawing_gesture(landmarks):
    """Index finger up, others (middle, ring, pinky) down."""
    index_up = is_finger_up(landmarks, mp_hands.HandLandmark.INDEX_FINGER_TIP, mp_hands.HandLandmark.INDEX_FINGER_PIP, mp_hands.HandLandmark.INDEX_FINGER_DIP)

    middle_down = not is_finger_up(landmarks, mp_hands.HandLandmark.MIDDLE_FINGER_TIP, mp_hands.HandLandmark.MIDDLE_FINGER_PIP, mp_hands.HandLandmark.MIDDLE_FINGER_DIP)
    ring_down = not is_finger_up(landmarks, mp_hands.HandLandmark.RING_FINGER_TIP, mp_hands.HandLandmark.RING_FINGER_PIP, mp_hands.HandLandmark.RING_FINGER_DIP)
    pinky_down = not is_finger_up(landmarks, mp_hands.HandLandmark.PINKY_TIP, mp_hands.HandLandmark.PINKY_PIP, mp_hands.HandLandmark.PINKY_DIP)

    # Optionally, ensure thumb is also somewhat curled or not interfering
    # thumb_curled = not is_finger_up(landmarks, mp_hands.HandLandmark.THUMB_TIP, mp_hands.HandLandmark.THUMB_IP, mp_hands.HandLandmark.THUMB_MCP)

    return index_up and middle_down and ring_down and pinky_down # and thumb_curled

def get_selected_color_gesture(landmarks):
    """
    Determines color based on finger gestures.
    - Index and Middle finger tips touching: Red
    - Index and Thumb tips touching: Blue
    - Fist (all fingers curled, thumb over index/middle): Green
    - Index and Pinky up, Middle and Ring down: Eraser (white)
    """
    index_tip = landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
    middle_tip = landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
    ring_tip = landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP]
    pinky_tip = landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP]
    thumb_tip = landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]

    index_pip = landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_PIP]
    middle_pip = landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_PIP]
    ring_pip = landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_PIP]
    pinky_pip = landmarks.landmark[mp_hands.HandLandmark.PINKY_PIP]
    thumb_ip = landmarks.landmark[mp_hands.HandLandmark.THUMB_IP]

    # Helper to check if two landmarks are close
    def are_landmarks_close(lm1, lm2, threshold=0.05): # Threshold is normalized distance
        return ((lm1.x - lm2.x)**2 + (lm1.y - lm2.y)**2)**0.5 < threshold

    # Index and Middle for Red
    if are_landmarks_close(index_tip, middle_tip, threshold=0.06): # Slightly larger threshold for tip touch
        return "red"

    # Index and Thumb for Blue
    if are_landmarks_close(index_tip, thumb_tip, threshold=0.06):
        return "blue"

    # Index and Pinky up for Eraser (White)
    # Ensure middle and ring are down
    index_up = is_finger_up(landmarks, mp_hands.HandLandmark.INDEX_FINGER_TIP, mp_hands.HandLandmark.INDEX_FINGER_PIP, mp_hands.HandLandmark.INDEX_FINGER_DIP)
    pinky_up = is_finger_up(landmarks, mp_hands.HandLandmark.PINKY_TIP, mp_hands.HandLandmark.PINKY_PIP, mp_hands.HandLandmark.PINKY_DIP)
    middle_down = not is_finger_up(landmarks, mp_hands.HandLandmark.MIDDLE_FINGER_TIP, mp_hands.HandLandmark.MIDDLE_FINGER_PIP, mp_hands.HandLandmark.MIDDLE_FINGER_DIP)
    ring_down = not is_finger_up(landmarks, mp_hands.HandLandmark.RING_FINGER_TIP, mp_hands.HandLandmark.RING_FINGER_PIP, mp_hands.HandLandmark.RING_FINGER_DIP)

    if index_up and pinky_up and middle_down and ring_down:
        return "white"

    # Fist for Green: All fingers curled, thumb over index/middle area
    # Check if all fingertips are below their respective PIP joints (curled)
    index_curled = index_tip.y > index_pip.y
    middle_curled = middle_tip.y > middle_pip.y
    ring_curled = ring_tip.y > ring_pip.y
    pinky_curled = pinky_tip.y > pinky_pip.y
    # Thumb curled: tip y greater than ip y, and tip x greater than ip x (for right hand, thumb curls inwards)
    thumb_curled = thumb_tip.y > thumb_ip.y and \
                   (abs(thumb_tip.x - index_pip.x) < 0.07 or abs(thumb_tip.x - middle_pip.x) < 0.07) # Thumb near index/middle PIP

    if index_curled and middle_curled and ring_curled and pinky_curled and thumb_curled:
        return "green"

    return None # No specific color gesture detected


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
    global drawing_color, brush_size, last_x, last_y

    ret, frame = cap.read()
    if not ret:
        root.after(10, main_loop) # Try again shortly
        return

    frame = cv2.flip(frame, 1)
    frame_height, frame_width, _ = frame.shape
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    active_drawing_gesture = False
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            # Optional: Draw landmarks on the frame for debugging
            # mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Color selection: Process this first
            new_color = get_selected_color_gesture(hand_landmarks)
            if new_color:
                drawing_color = new_color
                # Update color_status_label, ensuring correct fg for white/black
                label_fg = drawing_color if drawing_color not in ["white", "yellow"] else "black" # Avoid invisible text
                color_status_label.config(text=f"Color: {drawing_color.upper()}", fg=label_fg)

            # Drawing gesture detection
            if is_drawing_gesture(hand_landmarks):
                active_drawing_gesture = True
                ix, iy = get_landmark_coordinates(hand_landmarks, mp_hands.HandLandmark.INDEX_FINGER_TIP, frame_width, frame_height)

                # Get canvas dimensions safely
                c_width = canvas.winfo_width()
                c_height = canvas.winfo_height()

                if c_width > 1 and c_height > 1: # Ensure canvas is rendered
                    canvas_x = int(ix * (c_width / frame_width))
                    canvas_y = int(iy * (c_height / frame_height))
                else: # Fallback or skip if canvas not ready
                    canvas_x, canvas_y = ix, iy # Or simply don't draw this point

                if last_x is None or last_y is None: # Start of a new line segment
                    last_x, last_y = canvas_x, canvas_y

                current_brush_size = 15 if drawing_color == "white" else brush_size # Eraser size
                canvas.create_line(last_x, last_y, canvas_x, canvas_y, fill=drawing_color, width=current_brush_size, capstyle=tk.ROUND, smooth=tk.TRUE)
                last_x, last_y = canvas_x, canvas_y
            # else: # This specific hand is not making the drawing gesture
                # If we reset last_x, last_y here, multi-hand interaction for drawing might be tricky
                # It's better to reset if NO hand is making the gesture (done below)

    # If no hand is making the drawing gesture (or no hands detected), reset last drawing point
    if not active_drawing_gesture:
        last_x, last_y = None, None

    # Display the camera feed
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


Button(controls_frame, text="Red", bg="red", fg="white", command=lambda: set_color("red")).pack(side=tk.LEFT, padx=5)
Button(controls_frame, text="Blue", bg="blue", fg="white", command=lambda: set_color("blue")).pack(side=tk.LEFT, padx=5)
Button(controls_frame, text="Green", bg="green", fg="white", command=lambda: set_color("green")).pack(side=tk.LEFT, padx=5)
Button(controls_frame, text="Eraser", bg="lightgray", fg="black", command=lambda: set_color("white")).pack(side=tk.LEFT, padx=5) # Eraser button appearance

# Set initial color for the label, considering contrast for light colors
initial_label_fg = drawing_color if drawing_color not in ["white", "yellow"] else "black"
color_status_label = Label(controls_frame, text=f"Color: {drawing_color.upper()}", font=("Arial", 14), fg=initial_label_fg)
color_status_label.pack(side=tk.LEFT, padx=20)


# OpenCV Camera Setup
cap = cv2.VideoCapture(0)
# Set camera resolution (optional, but can help with performance and consistency)
# cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
# cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

if not cap.isOpened():
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
