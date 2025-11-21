// SignSpeak AI JavaScript - unified camera, UI and ASL processing

document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, looking for elements...');
    
    const video = document.getElementById('video');
    const startStop = document.getElementById('startStop');
    const startDetectionBtn = document.getElementById('start-detection-btn');
    const stopDetectionBtn = document.getElementById('stop-detection-btn');
    const speakBtn = document.getElementById('speak-btn');
    const resetBtn = document.getElementById('reset-btn');
    const textOutput = document.getElementById('textOutput');
    // Preferred translation element: explicit span with id 'translationText'
    // Fallbacks: span inside #textOutput or the #textOutput container itself
    const translationTextEl = document.getElementById('translationText') || document.querySelector('#textOutput span') || textOutput;
    
    console.log('Elements found:', {
        video: !!video,
        startStop: !!startStop, 
        textOutput: !!textOutput,
        translationText: !!translationTextEl
    });
    
    if (!video || !startStop || !textOutput) {
        console.error('Missing required elements!');
        return;
    }
    
    let stream = null;
    let running = false;
    let processingInterval = null;

    async function startStream() {
        try {
            stream = await navigator.mediaDevices.getUserMedia({ video: { width: { ideal: 1280 }, height: { ideal: 720 } }, audio: false });
            video.srcObject = stream;
            running = true;
            startStop.textContent = 'Stop';
            
            // Start ASL processing with reduced frequency to avoid overwhelming APIs
            processingInterval = setInterval(processCurrentFrame, 2000); // Process every 2 seconds instead of 1
            updateTextOutput('ASL Recognition Active - Show your gestures!');

            // Do one immediate processing pass so the UI updates without waiting for the interval
            try {
                processCurrentFrame();
            } catch (e) {
                console.warn('Immediate frame processing failed:', e);
            }
        } catch (err) {
            alert('Camera access denied or not available: ' + err.message);
        }
    }

    function stopStream() {
        if (stream) {
            stream.getTracks().forEach(t => t.stop());
            video.srcObject = null;
        }
        running = false;
        startStop.textContent = 'Start';
        
        // Stop ASL processing
        if (processingInterval) {
            clearInterval(processingInterval);
            processingInterval = null;
        }
        updateTextOutput('Camera stopped');
    }

    async function processCurrentFrame() {
        if (!video.videoWidth || !video.videoHeight || !running) {
            return;
        }
        
        console.log('Processing frame...');
        
        try {
            // Create a canvas to capture the current video frame
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            
            // Draw the current video frame to the canvas
            ctx.drawImage(video, 0, 0);
            
            // Convert canvas to base64 image data
            const imageData = canvas.toDataURL('image/jpeg', 0.8);
            
            console.log('Sending frame to backend...');
            
            // Send frame to backend for processing
            const response = await fetch('/process_frame', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ image: imageData })
            });
            
            const result = await response.json();
            console.log('🔄 Backend response received:', JSON.stringify(result, null, 2));
            
            // Always try to update UI elements if they exist
            const currentGesture = document.getElementById('currentGesture');
            const confidenceEl = document.getElementById('confidence'); 
            const gestureCount = document.getElementById('gestureCount');
            const translationText = translationTextEl; // Use resolved element from load
            
            console.log('🎯 UI Elements found:', {
                currentGesture: !!currentGesture,
                confidenceEl: !!confidenceEl,
                gestureCount: !!gestureCount,
                translationText: !!translationText
            });
            
            if (result.success) {
                // Update translation text
                if (result.translation) {
                    if (translationText) {
                        translationText.textContent = result.translation;
                        console.log('✅ Updated translation text to:', result.translation);
                    } else {
                        updateTextOutput(result.translation);
                        console.log('✅ Updated text output (fallback) to:', result.translation);
                    }
                }
                
                // Update gesture info if gesture detected
                if (result.gesture && result.gesture !== 'Unknown' && result.gesture !== null) {
                    const confidence = (result.confidence * 100).toFixed(1);
                    
                    if (currentGesture) {
                        // Add visual indicator for live preview vs confirmed detection
                        const prefix = result.live_preview ? "👁️ " : "✅ ";
                        currentGesture.textContent = prefix + result.gesture;
                        console.log('✅ Updated currentGesture to:', prefix + result.gesture);
                    }
                    if (confidenceEl) {
                        confidenceEl.textContent = `${confidence}%`;
                        console.log('✅ Updated confidence to:', `${confidence}%`);
                    }
                    
                    // Also update main text output for backup
                    if (!result.live_preview) {
                        updateTextOutput(`Detected: ${result.gesture} (${confidence}% confident)`);
                    }
                } else if (!result.detection_active && !result.live_preview) {
                    // Clear gesture info when no hand is detected and not in detection mode
                    if (currentGesture) currentGesture.textContent = 'None';
                    if (confidenceEl) confidenceEl.textContent = '0%';
                }
                
                // Update gesture count only for confirmed detections (not live preview)
                if (result.gesture_count !== undefined && gestureCount && !result.live_preview) {
                    gestureCount.textContent = result.gesture_count.toString();
                    console.log('✅ Updated gesture count to:', result.gesture_count);
                }
            } else {
                console.log('❌ Processing failed:', result);
            }
        } catch (error) {
            console.error('Error processing frame:', error);
        }
    }

    function updateTextOutput(message) {
            // Use resolved translation element if available, otherwise fall back to #textOutput
            if (translationTextEl) {
                translationTextEl.textContent = message;
            } else if (textOutput) {
                textOutput.innerHTML = `<p style="margin:0; color:var(--text-dark);">${message}</p>`;
            }
    }

    startStop.addEventListener('click', () => {
        if (running) stopStream(); else startStream();
    });

    // Initialize text output placeholder
    textOutput.innerHTML = '<p style="margin:0; color:var(--text-dark); opacity:0.6;">Start camera to begin ASL recognition...</p>';

    resetBtn.addEventListener('click', function() {
        if (running) {
            updateTextOutput('ASL Recognition Active - Show your gestures!');
        } else {
            textOutput.innerHTML = '<p style="margin:0; color:var(--text-dark); opacity:0.6;">Start camera to begin ASL recognition...</p>';
        }
        console.log('Reset button clicked');
    });

    speakBtn.addEventListener('click', function() {
        const text = textOutput.innerText || textOutput.textContent || 'Hello';
        if ('speechSynthesis' in window) {
            const utter = new SpeechSynthesisUtterance(text);
            window.speechSynthesis.speak(utter);
        } else {
            console.warn('Speech Synthesis not supported in this browser.');
        }
    });

    // Start Detection button handler
startDetectionBtn.addEventListener('click', function() {
    console.log('Start Detection button clicked');
    fetch('/start_detection', { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            console.log('Start detection response:', data);
            if (data.success) {
                updateTextOutput('🎯 Detection started - Show your gestures!');
            }
        })
        .catch(err => console.error('Start detection error:', err));
});

// Stop Detection button handler
stopDetectionBtn.addEventListener('click', function() {
    console.log('Stop Detection button clicked');
    fetch('/stop_detection', { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            console.log('Stop detection response:', data);
            if (data.success) {
                updateTextOutput('🛑 Detection stopped');
            }
        })
        .catch(err => console.error('Stop detection error:', err));
})});
