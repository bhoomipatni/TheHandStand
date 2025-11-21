from flask import Flask, render_template, request, jsonify
import cv2
import numpy as np
import base64
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Flask to use the frontend folders for static files and templates
app = Flask(__name__, static_folder='frontend/static', template_folder='frontend/templates')

# Global variables for lazy loading
pipeline = None

def get_pipeline():
    """Lazy load the ASL pipeline"""
    global pipeline
    if pipeline is None:
        try:
            from backend.pipeline import ASLPipeline
            print("🔄 Initializing ASL Pipeline...")
            pipeline = ASLPipeline()
            print("✅ ASL Pipeline ready!")
        except Exception as e:
            # Don't raise here — log and allow callers to handle the missing pipeline
            import traceback
            print("❌ Pipeline initialization failed:", e)
            traceback.print_exc()
            pipeline = None
    return pipeline

@app.route('/health')
def health_check():
    print("🏥 HEALTH CHECK - Server is responding")
    return {
        "status": "healthy",
        "message": "Flask server is running",
        "timestamp": str(__import__('datetime').datetime.now())
    }

@app.route('/')
def home():
    print("🏠 HOME ROUTE HIT - Loading main page")
    try:
        result = render_template('index.html')
        print("✅ Template rendered successfully")
        return result
    except Exception as e:
        print(f"❌ Template error: {str(e)}")
        return f"Template error: {str(e)}<br><a href='/debug'>Try debug page</a>"

@app.route('/debug')
def debug():
    print("🐛 DEBUG ROUTE HIT")
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Debug - The HandStand</title>
    </head>
    <body>
        <h1>🤟 The HandStand - Debug Page</h1>
        <p>This is a hardcoded HTML page to test if Flask is working.</p>
        <p>If you see this, the server is working but there might be a template issue.</p>
        <p>Try the main page: <a href="/">Main Page</a></p>
        <p>Try simple test: <a href="/simple">Simple Test</a></p>
    </body>
    </html>
    """

@app.route('/simple')
def simple_test():
    return """
    <h1>🤟 The HandStand - Simple Test</h1>
    <p>If you can see this, the Flask app is working!</p>
    <p>Main interface should be at <a href="/">http://127.0.0.1:5001</a></p>
    """

@app.route('/test_connection')
def test_connection():
    print("=== TEST CONNECTION ENDPOINT HIT ===")
    try:
        # Test if pipeline can be initialized
        current_pipeline = get_pipeline()
        return jsonify({
            "status": "success", 
            "message": "Backend is working",
            "pipeline_loaded": current_pipeline is not None
        })
    except Exception as e:
        print(f"Test connection error: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        })

@app.route('/test')
def test():
    print("Test endpoint hit!")
    return jsonify({"status": "working", "message": "Server is responding"})

@app.route('/testpage')
def testpage():
    return "<h1>Flask is working!</h1><p>No template needed.</p>"

@app.route('/process_frame', methods=['POST'])
def process_frame():
    try:
        # Get the image data from the request
        data = request.json
        image_data = data['image']
        
        # Decode the base64 image
        header, encoded = image_data.split(',', 1)
        image_bytes = base64.b64decode(encoded)
        nparr = np.frombuffer(image_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # Process the frame using lazy-loaded pipeline
        current_pipeline = get_pipeline()
        if current_pipeline is None:
            print("❌ process_frame: pipeline not available")
            return jsonify({'success': False, 'error': 'Backend pipeline initialization failed'}), 500

        result = current_pipeline.process_frame(frame)

        # Debug: Print what we're sending to frontend
        print(f"🔄 Sending to frontend: {result}")

        return jsonify(result)
        
    except Exception as e:
        print(f"Error processing frame: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/speak', methods=['POST'])
def speak_text():
    try:
        data = request.json
        text = data.get('text', '')
        
        if not text:
            return jsonify({
                'success': False,
                'error': 'No text provided'
            })
        
        # Use lazy-loaded pipeline for speech
        current_pipeline = get_pipeline()
        if current_pipeline is None:
            return jsonify({'success': False, 'error': 'Backend pipeline initialization failed'}), 500

        # Get the speech synthesizer from the pipeline
        if hasattr(current_pipeline, 'speech_synthesizer') and current_pipeline.speech_synthesizer:
            try:
                current_pipeline.speech_synthesizer.speak_text(text)
                return jsonify({'success': True, 'message': f'Speaking: "{text}"'})
            except Exception as e:
                print(f"Speech synthesis error: {e}")
                return jsonify({'success': False, 'error': f'Speech synthesis failed: {str(e)}'}), 500
        else:
            return jsonify({'success': False, 'error': 'Speech synthesizer not available'}), 503
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/start_detection', methods=['POST'])
def start_detection():
    try:
        current_pipeline = get_pipeline()
        if current_pipeline is None:
            return jsonify({'success': False, 'error': 'Backend pipeline initialization failed'}), 500

        current_pipeline.start_detection()
        return jsonify({'success': True, 'message': 'Detection started - show your gesture!'})
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/stop_detection', methods=['POST'])
def stop_detection():
    try:
        current_pipeline = get_pipeline()
        if current_pipeline is None:
            return jsonify({'success': False, 'error': 'Backend pipeline initialization failed'}), 500

        current_pipeline.stop_detection()
        return jsonify({'success': True, 'message': 'Detection stopped'})
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/reset', methods=['POST'])
def reset_demo():
    try:
        # Use lazy-loaded pipeline for reset
        current_pipeline = get_pipeline()
        if current_pipeline is None:
            return jsonify({'success': False, 'error': 'Backend pipeline initialization failed'}), 500

        current_pipeline.reset_conversation()
        return jsonify({'success': True, 'message': 'Demo reset - ready for new gestures!'})
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5001))
    print("=" * 50)
    print("🚀 Starting The HandStand Flask App")
    print(f"📁 Templates folder: {os.path.abspath(app.template_folder)}")
    print(f"📁 Static folder: {os.path.abspath(app.static_folder)}")
    print(f"📍 Main interface: http://0.0.0.0:{port}/")
    print(f"🔍 Debug page: http://0.0.0.0:{port}/debug")  
    print(f"🧪 Simple test: http://0.0.0.0:{port}/simple")
    print("💡 Components will load lazily when first accessed")
    print("🚫 Debug mode OFF to prevent double-loading")
    print("=" * 50)
    app.run(host='0.0.0.0', port=port, debug=False)