class GesturePaintingApp {
    constructor() {
        this.video = document.getElementById('camera');
        this.handCanvas = document.getElementById('hand-canvas');
        this.paintingCanvas = document.getElementById('painting-canvas');
        this.handCtx = this.handCanvas.getContext('2d');
        this.paintingCtx = this.paintingCanvas.getContext('2d');
        
        // App state
        this.currentMode = 'draw'; // 'draw', 'erase', 'select'
        this.currentColor = '#000000';
        this.brushSize = 5;
        this.isDrawing = false;
        this.lastPoint = null;
        
        // Hand tracking
        this.hands = null;
        this.camera = null;
        this.handDetected = false;
        this.gestureHistory = [];
        
        // Debug mode
        this.debugMode = true;
        
        // Canvas setup
        this.setupCanvas();
        this.setupEventListeners();
        this.initializeHandTracking();
        
        // Add debug info to page
        this.addDebugInfo();
    }

    setupCanvas() {
        // Set canvas dimensions
        this.paintingCanvas.width = this.paintingCanvas.offsetWidth;
        this.paintingCanvas.height = this.paintingCanvas.offsetHeight;
        this.handCanvas.width = this.handCanvas.offsetWidth;
        this.handCanvas.height = this.handCanvas.offsetHeight;
        
        // Set painting canvas background
        this.paintingCtx.fillStyle = 'white';
        this.paintingCtx.fillRect(0, 0, this.paintingCanvas.width, this.paintingCanvas.height);
        
        // Set drawing styles
        this.paintingCtx.lineCap = 'round';
        this.paintingCtx.lineJoin = 'round';
    }

    setupEventListeners() {
        // Tool buttons
        document.querySelectorAll('.tool-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.setTool(e.target.dataset.tool);
            });
        });

        // Color buttons
        document.querySelectorAll('.color-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.setColor(e.target.dataset.color);
            });
        });

        // Brush size
        const brushSlider = document.getElementById('brush-size');
        const brushValue = document.getElementById('brush-size-value');
        brushSlider.addEventListener('input', (e) => {
            this.brushSize = parseInt(e.target.value);
            brushValue.textContent = `${this.brushSize}px`;
        });

        // Action buttons
        document.getElementById('clear-btn').addEventListener('click', () => {
            this.clearCanvas();
        });

        document.getElementById('save-btn').addEventListener('click', () => {
            this.saveImage();
        });

        document.getElementById('test-btn').addEventListener('click', () => {
            this.testHandTracking();
        });

        document.getElementById('camera-test-btn').addEventListener('click', () => {
            this.testCamera();
        });

        // Window resize
        window.addEventListener('resize', () => {
            this.setupCanvas();
        });
    }

    async initializeHandTracking() {
        try {
            console.log('🔍 Starting hand tracking initialization...');
            
            // Wait for MediaPipe to load
            await this.waitForMediaPipe();
            
            // Initialize camera first
            await this.initializeCamera();
            
            // Initialize MediaPipe Hands
            await this.initializeMediaPipeHands();
            
            console.log('✅ Hand tracking initialization complete');
            this.updateHandStatus('Hand tracking ready');

        } catch (error) {
            console.error('❌ Error initializing hand tracking:', error);
            this.updateHandStatus('Error: ' + error.message);
            
            // Try fallback method
            this.tryFallbackMethod();
        }
    }

    async waitForMediaPipe() {
        console.log('⏳ Waiting for MediaPipe to load...');
        
        // Wait up to 10 seconds for MediaPipe to load
        for (let i = 0; i < 100; i++) {
            if (typeof Hands !== 'undefined' && typeof Camera !== 'undefined') {
                console.log('✅ MediaPipe libraries loaded');
                return;
            }
            await new Promise(resolve => setTimeout(resolve, 100));
        }
        
        throw new Error('MediaPipe libraries failed to load. Please refresh the page.');
    }

    async initializeCamera() {
        console.log('📹 Initializing camera...');
        
        try {
            // Get camera stream using WebRTC
            const stream = await navigator.mediaDevices.getUserMedia({
                video: {
                    width: { ideal: 640 },
                    height: { ideal: 480 },
                    facingMode: 'user'
                }
            });
            
            this.video.srcObject = stream;
            this.video.play();
            
            // Wait for video to be ready
            await new Promise((resolve) => {
                this.video.onloadedmetadata = resolve;
            });
            
            console.log('✅ Camera initialized successfully');
            console.log('📐 Video dimensions:', this.video.videoWidth, 'x', this.video.videoHeight);
            
        } catch (error) {
            console.error('❌ Camera initialization failed:', error);
            throw new Error('Camera access denied. Please allow camera permissions.');
        }
    }

    async initializeMediaPipeHands() {
        console.log('🤖 Initializing MediaPipe Hands...');
        
        this.hands = new Hands({
            locateFile: (file) => {
                console.log('📁 Loading MediaPipe file:', file);
                return `https://cdn.jsdelivr.net/npm/@mediapipe/hands@0.4.1646424915/${file}`;
            }
        });

        this.hands.setOptions({
            maxNumHands: 1,
            modelComplexity: 0, // Use simpler model for better performance
            minDetectionConfidence: 0.3,
            minTrackingConfidence: 0.3
        });

        this.hands.onResults((results) => {
            this.onHandResults(results);
        });

        // Start processing frames
        this.startFrameProcessing();
    }

    startFrameProcessing() {
        console.log('🔄 Starting frame processing...');
        
        const processFrame = async () => {
            if (this.video.readyState === this.video.HAVE_ENOUGH_DATA) {
                try {
                    await this.hands.send({ image: this.video });
                } catch (error) {
                    console.error('❌ Error processing frame:', error);
                }
            }
            requestAnimationFrame(processFrame);
        };
        
        processFrame();
    }

    async tryFallbackMethod() {
        console.log('🔄 Trying fallback method...');
        
        try {
            // Try with even lower settings
            this.hands = new Hands({
                locateFile: (file) => {
                    return `https://cdn.jsdelivr.net/npm/@mediapipe/hands@0.4.1646424915/${file}`;
                }
            });

            this.hands.setOptions({
                maxNumHands: 1,
                modelComplexity: 0,
                minDetectionConfidence: 0.1, // Very low threshold
                minTrackingConfidence: 0.1
            });

            this.hands.onResults((results) => {
                this.onHandResults(results);
            });

            this.startFrameProcessing();
            
            console.log('✅ Fallback method successful');
            this.updateHandStatus('Hand tracking (fallback mode)');

        } catch (error) {
            console.error('❌ Fallback method failed:', error);
            this.updateHandStatus('Hand tracking failed');
            alert('Hand tracking failed to initialize. Please refresh the page and try again.');
        }
    }

    onHandResults(results) {
        this.handCtx.clearRect(0, 0, this.handCanvas.width, this.handCanvas.height);

        // Debug: Log results structure
        if (this.debugCounter === undefined) this.debugCounter = 0;
        this.debugCounter++;
        if (this.debugCounter % 30 === 0) { // Log every 30 frames
            console.log('📊 Hand results:', {
                multiHandLandmarks: results.multiHandLandmarks?.length || 0,
                multiHandedness: results.multiHandedness?.length || 0,
                hasResults: !!results
            });
        }

        if (results.multiHandLandmarks && results.multiHandLandmarks.length > 0) {
            this.handDetected = true;
            this.updateHandStatus('Hand detected');
            
            const landmarks = results.multiHandLandmarks[0];
            console.log('👋 Processing hand landmarks:', landmarks.length);
            
            this.drawHandLandmarks(landmarks);
            this.processHandGestures(landmarks);
        } else {
            this.handDetected = false;
            this.updateHandStatus('No hand detected');
            this.isDrawing = false;
            this.updateDebugInfo(null, null);
        }
    }

    drawHandLandmarks(landmarks) {
        // Draw hand landmarks
        for (const landmark of landmarks) {
            const x = landmark.x * this.handCanvas.width;
            const y = landmark.y * this.handCanvas.height;
            
            this.handCtx.beginPath();
            this.handCtx.arc(x, y, 3, 0, 2 * Math.PI);
            this.handCtx.fillStyle = '#00ff00';
            this.handCtx.fill();
        }

        // Draw connections
        this.drawHandConnections(landmarks);
    }

    drawHandConnections(landmarks) {
        const connections = [
            [0, 1], [1, 2], [2, 3], [3, 4], // thumb
            [0, 5], [5, 6], [6, 7], [7, 8], // index
            [5, 9], [9, 10], [10, 11], [11, 12], // middle
            [9, 13], [13, 14], [14, 15], [15, 16], // ring
            [13, 17], [17, 18], [18, 19], [19, 20], // pinky
            [0, 17], [5, 9], [9, 13], [13, 17] // palm
        ];

        this.handCtx.strokeStyle = '#00ff00';
        this.handCtx.lineWidth = 2;

        for (const [start, end] of connections) {
            const startX = landmarks[start].x * this.handCanvas.width;
            const startY = landmarks[start].y * this.handCanvas.height;
            const endX = landmarks[end].x * this.handCanvas.width;
            const endY = landmarks[end].y * this.handCanvas.height;

            this.handCtx.beginPath();
            this.handCtx.moveTo(startX, startY);
            this.handCtx.lineTo(endX, endY);
            this.handCtx.stroke();
        }
    }

    processHandGestures(landmarks) {
        const gesture = this.recognizeGesture(landmarks);
        this.gestureHistory.push(gesture);
        
        // Keep only last 5 gestures for stability
        if (this.gestureHistory.length > 5) {
            this.gestureHistory.shift();
        }

        // Use most common gesture in history for stability
        const mostCommonGesture = this.getMostCommonGesture();
        
        // Update debug info
        this.updateDebugInfo(landmarks, mostCommonGesture);
        
        this.handleGesture(mostCommonGesture, landmarks);
    }

    recognizeGesture(landmarks) {
        const fingerTips = [4, 8, 12, 16, 20]; // thumb, index, middle, ring, pinky
        const fingerBases = [2, 5, 9, 13, 17];
        
        const extendedFingers = [];
        
        // Debug: Log landmark positions
        if (this.gestureDebugCounter === undefined) this.gestureDebugCounter = 0;
        this.gestureDebugCounter++;
        
        // Always log finger positions for debugging
        console.log('🔍 Analyzing finger positions...');
        
        for (let i = 0; i < fingerTips.length; i++) {
            const tip = landmarks[fingerTips[i]];
            const base = landmarks[fingerBases[i]];
            
            if (!tip || !base) {
                console.warn('⚠️ Missing landmark for finger', i);
                extendedFingers.push(false);
                continue;
            }
            
            // Improved finger detection logic
            let isExtended;
            if (i === 0) { // thumb - check horizontal position
                isExtended = tip.x > base.x;
                console.log(`👍 Thumb: tip.x(${tip.x.toFixed(3)}) > base.x(${base.x.toFixed(3)}) = ${isExtended}`);
            } else { // other fingers - check vertical position
                isExtended = tip.y < base.y;
                console.log(`👆 Finger ${i}: tip.y(${tip.y.toFixed(3)}) < base.y(${base.y.toFixed(3)}) = ${isExtended}`);
            }
            extendedFingers.push(isExtended);
        }

        // More flexible gesture recognition
        const [thumb, index, middle, ring, pinky] = extendedFingers;
        
        console.log('🎯 Final finger states:', { thumb, index, middle, ring, pinky });

        // Simplified gesture recognition with more tolerance
        const extendedCount = extendedFingers.filter(f => f).length;
        console.log(`📊 Extended fingers count: ${extendedCount}`);

        // Alternative gesture detection using finger distances
        const indexTip = landmarks[8];
        const indexBase = landmarks[5];
        const thumbTip = landmarks[4];
        const thumbBase = landmarks[2];
        
        // Calculate finger extension distances
        const indexExtension = Math.abs(indexTip.y - indexBase.y);
        const thumbExtension = Math.abs(thumbTip.x - thumbBase.x);
        
        console.log('📏 Finger extensions:', {
            indexExtension: indexExtension.toFixed(3),
            thumbExtension: thumbExtension.toFixed(3)
        });

        // Gesture recognition with more tolerance
        if (index && !thumb && !middle && !ring && !pinky) {
            console.log('✅ Detected: POINT gesture (index only)');
            return 'point';
        } else if (extendedCount >= 4) {
            console.log('✅ Detected: OPEN_PALM gesture (4+ fingers)');
            return 'open_palm';
        } else if (extendedCount === 0) {
            console.log('✅ Detected: FIST gesture (no fingers)');
            return 'fist';
        } else if (thumb && index && extendedCount === 2) {
            console.log('✅ Detected: PINCH gesture (thumb + index)');
            return 'pinch';
        } else if (indexExtension > 0.1 && extendedCount === 1) {
            console.log('✅ Detected: POINT gesture (by extension)');
            return 'point';
        } else if (extendedCount >= 3) {
            console.log('✅ Detected: OPEN_PALM gesture (3+ fingers)');
            return 'open_palm';
        } else {
            console.log('❓ Unknown gesture pattern:', { thumb, index, middle, ring, pinky });
            console.log('💡 Try making clearer gestures or check lighting');
            return 'unknown';
        }
    }

    getMostCommonGesture() {
        const counts = {};
        this.gestureHistory.forEach(gesture => {
            counts[gesture] = (counts[gesture] || 0) + 1;
        });
        
        return Object.keys(counts).reduce((a, b) => counts[a] > counts[b] ? a : b);
    }

    handleGesture(gesture, landmarks) {
        const indexTip = landmarks[8]; // Index finger tip
        
        // Debug gesture detection
        if (this.gestureDebugCounter % 60 === 0) {
            console.log('🎭 Detected gesture:', gesture);
        }
        
        if (!indexTip) {
            console.warn('⚠️ No index tip landmark found');
            return;
        }
        
        switch (gesture) {
            case 'point':
                console.log('✏️ Switching to drawing mode');
                this.setMode('draw');
                this.handleDrawing(indexTip);
                break;
            case 'open_palm':
                console.log('🧽 Switching to erasing mode');
                this.setMode('erase');
                this.handleErasing(indexTip);
                break;
            case 'pinch':
                console.log('👆 Switching to selection mode');
                this.setMode('select');
                this.handleSelection(indexTip);
                break;
            case 'fist':
                console.log('🗑️ Clearing canvas');
                this.clearCanvas();
                break;
            default:
                this.isDrawing = false;
                break;
        }
    }

    handleDrawing(landmark) {
        const x = landmark.x * this.paintingCanvas.width;
        const y = landmark.y * this.paintingCanvas.height;
        
        if (this.currentMode === 'draw') {
            this.paintingCtx.strokeStyle = this.currentColor;
            this.paintingCtx.lineWidth = this.brushSize;
            
            if (!this.isDrawing) {
                this.isDrawing = true;
                this.lastPoint = { x, y };
            } else {
                this.paintingCtx.beginPath();
                this.paintingCtx.moveTo(this.lastPoint.x, this.lastPoint.y);
                this.paintingCtx.lineTo(x, y);
                this.paintingCtx.stroke();
                this.lastPoint = { x, y };
            }
        }
    }

    handleErasing(landmark) {
        const x = landmark.x * this.paintingCanvas.width;
        const y = landmark.y * this.paintingCanvas.height;
        
        if (this.currentMode === 'erase') {
            this.paintingCtx.strokeStyle = 'white';
            this.paintingCtx.lineWidth = this.brushSize * 2;
            
            if (!this.isDrawing) {
                this.isDrawing = true;
                this.lastPoint = { x, y };
            } else {
                this.paintingCtx.beginPath();
                this.paintingCtx.moveTo(this.lastPoint.x, this.lastPoint.y);
                this.paintingCtx.lineTo(x, y);
                this.paintingCtx.stroke();
                this.lastPoint = { x, y };
            }
        }
    }

    handleSelection(landmark) {
        const x = landmark.x * this.paintingCanvas.width;
        const y = landmark.y * this.paintingCanvas.height;
        
        if (this.currentMode === 'select') {
            // Check if pointing at color palette
            const colorButtons = document.querySelectorAll('.color-btn');
            colorButtons.forEach((btn, index) => {
                const rect = btn.getBoundingClientRect();
                const canvasRect = this.paintingCanvas.getBoundingClientRect();
                
                // Convert canvas coordinates to screen coordinates
                const screenX = (x / this.paintingCanvas.width) * canvasRect.width + canvasRect.left;
                const screenY = (y / this.paintingCanvas.height) * canvasRect.height + canvasRect.top;
                
                if (screenX >= rect.left && screenX <= rect.right && 
                    screenY >= rect.top && screenY <= rect.bottom) {
                    this.setColor(btn.dataset.color);
                }
            });
        }
    }

    setMode(mode) {
        if (this.currentMode !== mode) {
            this.currentMode = mode;
            this.updateModeDisplay();
            
            // Update tool buttons
            document.querySelectorAll('.tool-btn').forEach(btn => {
                btn.classList.remove('active');
            });
            document.querySelector(`[data-tool="${mode}"]`).classList.add('active');
        }
    }

    setTool(tool) {
        this.setMode(tool);
    }

    setColor(color) {
        this.currentColor = color;
        
        // Update color buttons
        document.querySelectorAll('.color-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-color="${color}"]`).classList.add('active');
    }

    updateModeDisplay() {
        const modeElement = document.getElementById('current-mode');
        const modeNames = {
            'draw': 'Drawing Mode',
            'erase': 'Erasing Mode',
            'select': 'Selection Mode'
        };
        
        modeElement.textContent = modeNames[this.currentMode];
        modeElement.parentElement.classList.add('mode-change');
        
        setTimeout(() => {
            modeElement.parentElement.classList.remove('mode-change');
        }, 300);
    }

    updateHandStatus(status) {
        document.getElementById('hand-status').textContent = status;
    }

    clearCanvas() {
        this.paintingCtx.fillStyle = 'white';
        this.paintingCtx.fillRect(0, 0, this.paintingCanvas.width, this.paintingCanvas.height);
    }

    saveImage() {
        const link = document.createElement('a');
        link.download = 'gesture-painting.png';
        link.href = this.paintingCanvas.toDataURL();
        link.click();
    }

    addDebugInfo() {
        // Add debug panel to the page
        const debugPanel = document.createElement('div');
        debugPanel.id = 'debug-panel';
        debugPanel.style.cssText = `
            position: fixed;
            top: 10px;
            right: 10px;
            background: rgba(0, 0, 0, 0.8);
            color: white;
            padding: 10px;
            border-radius: 5px;
            font-family: monospace;
            font-size: 12px;
            z-index: 1000;
            max-width: 300px;
        `;
        debugPanel.innerHTML = `
            <div><strong>Debug Info:</strong></div>
            <div id="debug-hand-status">Hand: Unknown</div>
            <div id="debug-gesture">Gesture: None</div>
            <div id="debug-mode">Mode: Drawing</div>
            <div id="debug-coordinates">Coords: (0, 0)</div>
        `;
        document.body.appendChild(debugPanel);
    }

    updateDebugInfo(landmarks = null, gesture = null) {
        if (!this.debugMode) return;
        
        const handStatus = document.getElementById('debug-hand-status');
        const gestureInfo = document.getElementById('debug-gesture');
        const modeInfo = document.getElementById('debug-mode');
        const coordInfo = document.getElementById('debug-coordinates');
        
        handStatus.textContent = `Hand: ${this.handDetected ? 'Detected' : 'Not detected'}`;
        gestureInfo.textContent = `Gesture: ${gesture || 'None'}`;
        modeInfo.textContent = `Mode: ${this.currentMode}`;
        
        if (landmarks && landmarks[8]) {
            const x = Math.round(landmarks[8].x * 100);
            const y = Math.round(landmarks[8].y * 100);
            coordInfo.textContent = `Coords: (${x}%, ${y}%)`;
        }
    }

    testHandTracking() {
        console.log('🧪 Starting hand tracking test...');
        
        // Test if MediaPipe is loaded
        if (typeof Hands === 'undefined') {
            console.error('❌ MediaPipe Hands not loaded');
            alert('MediaPipe Hands library not loaded. Please refresh the page.');
            return;
        }
        
        // Test if camera is working
        if (!this.video.srcObject) {
            console.error('❌ Camera not initialized');
            alert('Camera not initialized. Please check camera permissions.');
            return;
        }
        
        console.log('✅ Basic tests passed');
        console.log('📹 Video element:', this.video);
        console.log('🎥 Camera stream:', this.video.srcObject);
        console.log('📐 Video dimensions:', this.video.videoWidth, 'x', this.video.videoHeight);
        console.log('🎬 Video ready state:', this.video.readyState);
        console.log('⏯️ Video playing:', !this.video.paused);
        
        // Test hand detection
        if (this.handDetected) {
            console.log('✅ Hand is currently detected');
        } else {
            console.log('❌ No hand currently detected');
            console.log('💡 Try positioning your hand in front of the camera');
        }
        
        // Test MediaPipe Hands
        if (this.hands) {
            console.log('✅ MediaPipe Hands initialized');
            console.log('🤖 Hands options:', this.hands.getOptions());
        } else {
            console.log('❌ MediaPipe Hands not initialized');
        }
        
        // Show test instructions
        alert('Hand tracking test started!\n\nCheck the console for detailed information.\n\nTry these gestures:\n1. Point with index finger\n2. Open palm\n3. Make a fist\n4. Pinch gesture\n\nMake sure your hand is clearly visible in the camera view.');
    }

    async testCamera() {
        console.log('📹 Testing camera...');
        
        try {
            // Test camera access
            const stream = await navigator.mediaDevices.getUserMedia({
                video: {
                    width: { ideal: 640 },
                    height: { ideal: 480 }
                }
            });
            
            console.log('✅ Camera access successful');
            console.log('📹 Stream tracks:', stream.getTracks());
            
            // Test video element
            const testVideo = document.createElement('video');
            testVideo.srcObject = stream;
            testVideo.play();
            
            setTimeout(() => {
                console.log('✅ Video playback test successful');
                console.log('📐 Test video dimensions:', testVideo.videoWidth, 'x', testVideo.videoHeight);
                
                // Stop the test stream
                stream.getTracks().forEach(track => track.stop());
                
                alert('Camera test successful!\n\nVideo dimensions: ' + testVideo.videoWidth + 'x' + testVideo.videoHeight);
            }, 2000);
            
        } catch (error) {
            console.error('❌ Camera test failed:', error);
            alert('Camera test failed: ' + error.message);
        }
    }
}

// Initialize the app when the page loads
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 Starting Gesture Painting App...');
    
    // Check if MediaPipe libraries are loaded
    setTimeout(() => {
        if (typeof Hands === 'undefined') {
            console.error('❌ MediaPipe Hands not loaded!');
            alert('MediaPipe Hands library failed to load. Please check your internet connection and refresh the page.');
        } else {
            console.log('✅ MediaPipe Hands library loaded successfully');
        }
        
        if (typeof Camera === 'undefined') {
            console.error('❌ MediaPipe Camera not loaded!');
            alert('MediaPipe Camera library failed to load. Please check your internet connection and refresh the page.');
        } else {
            console.log('✅ MediaPipe Camera library loaded successfully');
        }
    }, 2000);
    
    new GesturePaintingApp();
}); 