# 🎨 Gesture Painting App

A web-based painting application that uses computer vision to track hand gestures and movements for drawing. The app uses MediaPipe Hands for real-time hand tracking and gesture recognition.

## Features

- **Real-time hand tracking** using your computer's camera
- **Gesture-based controls** for different painting modes
- **Three painting modes**: Drawing, Erasing, and Selection
- **Color palette** with 8 different colors
- **Adjustable brush size** from 1px to 50px
- **Save and clear functionality**
- **Modern, responsive UI** with glassmorphism design

## Gesture Controls

| Gesture | Action |
|---------|--------|
| 👆 **Point with index finger** | Drawing mode - Draw on the canvas |
| ✋ **Open palm** | Erasing mode - Erase from the canvas |
| 👌 **Pinch gesture** | Selection mode - Select colors and tools |
| ✊ **Fist** | Clear the entire canvas |

## How to Use

1. **Open the app** in a modern web browser (Chrome, Firefox, Safari, Edge)
2. **Allow camera access** when prompted
3. **Position your hand** in front of the camera
4. **Use gestures** to control the painting modes:
   - Point with your index finger to draw
   - Open your palm to erase
   - Make a pinch gesture to select colors/tools
   - Make a fist to clear the canvas

## Technical Details

### Technologies Used
- **HTML5 Canvas** for drawing
- **MediaPipe Hands** for hand tracking
- **WebRTC** for camera access
- **CSS3** with modern styling and animations
- **Vanilla JavaScript** for functionality

### Browser Requirements
- Modern browser with WebRTC support
- HTTPS connection (required for camera access)
- Camera permissions

### Performance Notes
- The app works best with good lighting
- Keep your hand clearly visible to the camera
- Maintain a reasonable distance from the camera (20-50cm)
- The gesture recognition uses a history buffer for stability

## File Structure

```
Paint/
├── index.html          # Main HTML file
├── styles.css          # CSS styling
├── script.js           # JavaScript functionality
└── README.md          # This file
```

## Getting Started

1. Clone or download the project files
2. Open `index.html` in a web browser
3. Allow camera permissions when prompted
4. Start painting with your hand gestures!

## Troubleshooting

### Camera Not Working
- Make sure you're using HTTPS or localhost
- Check that camera permissions are granted
- Try refreshing the page

### Hand Tracking Issues
- Ensure good lighting conditions
- Keep your hand clearly visible to the camera
- Try adjusting your distance from the camera
- Make sure your hand is not too close or too far

### Gesture Recognition Problems
- Make clear, deliberate gestures
- Hold gestures steady for a moment
- Check that your hand is fully visible in the camera view

## Browser Compatibility

- ✅ Chrome 88+
- ✅ Firefox 85+
- ✅ Safari 14+
- ✅ Edge 88+

## License

This project is open source and available under the MIT License.

## Contributing

Feel free to contribute improvements, bug fixes, or new features! 