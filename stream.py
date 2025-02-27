from flask import Flask, Response
import cv2
from picamera2 import Picamera2

# Initialize Flask app
app = Flask(__name__)

# Delay initializing the camera
picam2 = None

def initialize_camera():
    global picam2
    if picam2 is None:
        picam2 = Picamera2()
        video_config = picam2.create_video_configuration(main={"size": (1456, 1088)})
        picam2.configure(video_config)
        picam2.start()

def generate_frames():
    """Capture frames from Picamera2 and stream as MJPEG"""
    initialize_camera()
    while True:
        # Capture a frame from the camera
        frame = picam2.capture_array()
       
        # Convert from RGB to BGR if necessary (OpenCV uses BGR by default)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
       
        # Encode the frame to JPEG
        _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 95]) # Increase quality (default is ~75)
       
        # Yield the frame as a byte stream for MJPEG
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
       
@app.route('/video_feed')
def video_feed():
    """Route to access the MJPEG stream"""
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=4000, debug=True)
