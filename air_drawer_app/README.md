# Air Painter - Draw with Hand Gestures

Unleash your inner artist with Air Painter! This Python application allows you to draw on a digital canvas simply by moving your index fingertip in the air, captured through your webcam. Select different colors and an eraser using intuitive hand gestures.

## Features

*   **Air Drawing:** Draw lines on the canvas by moving your extended index finger.
*   **Gesture-Based Color Selection:**
    *   **Red:** Touch your Index fingertip to your Middle fingertip.
    *   **Blue:** Touch your Index fingertip to your Thumb tip.
    *   **Green:** Make a fist (all fingers curled, thumb across the front).
    *   **Eraser (White):** Extend your Index and Pinky fingers, keeping Middle and Ring fingers curled down.
*   **Real-time Camera Feed:** See yourself and your gestures in a separate window.
*   **GUI Controls:**
    *   A large canvas for drawing.
    *   Buttons for manually selecting colors (useful for debugging or alternative input).
    *   A label displaying the currently selected color.

## Dependencies

This project uses the following Python libraries:

*   `opencv-python`: For camera access and image processing.
*   `mediapipe`: For advanced hand tracking and landmark detection.
*   `tkinter`: For the graphical user interface (usually included with Python).
*   `numpy`: Used by OpenCV and MediaPipe.

All necessary dependencies are listed in the `requirements.txt` file.

## Setup Instructions

1.  **Clone or Download the Repository:**
    Get the project files onto your local machine.

2.  **Create a Virtual Environment (Recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install Dependencies:**
    Navigate to the `air_drawer_app` directory in your terminal and run:
    ```bash
    pip install -r requirements.txt
    ```

## How to Run the Application

1.  Ensure your webcam is connected and accessible.
2.  Navigate to the `air_drawer_app` directory in your terminal.
3.  Run the main script:
    ```bash
    python main.py
    ```
    Two windows should appear:
    *   One titled "Air Painter" (the Tkinter GUI with the canvas).
    *   One titled "Camera Feed" (showing your webcam input).

## Gesture Guide

Hold your hand clearly in view of the camera.

*   **To Draw:**
    *   Extend only your **Index Finger** (pointer finger). Other fingers (Middle, Ring, Pinky) should be curled down.
    *   Move your index fingertip to draw on the canvas.

*   **To Change Colors/Use Eraser:**
    Make one of the following gestures. The color status label in the GUI will update.
    *   **Red:** Touch your **Index Finger tip** to your **Middle Finger tip**.
    *   **Blue:** Touch your **Index Finger tip** to your **Thumb tip**.
    *   **Green:** Make a **Fist** (all fingers curled inwards, with your thumb resting over your curled fingers).
    *   **Eraser (White):** Extend your **Index Finger** and **Pinky Finger** upwards, while keeping your Middle and Ring fingers curled down.

    Once a color is selected, return to the drawing gesture to continue drawing with the new color.

## Troubleshooting/Notes

*   **Camera Access:** If the application fails to open the camera, ensure no other application is currently using it. You might see an "Error: Cannot open camera" message in the console.
*   **Lighting:** Good, consistent lighting will improve hand tracking accuracy. Avoid very dark environments or strong backlighting.
*   **Gesture Recognition:**
    *   Make clear and distinct gestures.
    *   If gestures are not being recognized reliably, you might need to adjust the sensitivity thresholds within the `main.py` code (e.g., `are_landmarks_close` threshold, or the logic in `is_finger_up`).
    *   The hand tracking works best when most of your hand is visible.
*   **Performance:** If the application runs slowly, try closing other resource-intensive programs. You can also try reducing the camera resolution (commented out lines in `main.py` for `cap.set()` can be enabled and adjusted).
*   **Exiting:** Close the "Air Painter" Tkinter window to quit the application. This will also close the camera feed window and release the camera.

---

Happy Drawing!
