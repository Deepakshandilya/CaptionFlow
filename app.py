from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO
from vosk import Model, KaldiRecognizer
import pyaudio
import json
import os
from collections import deque

app = Flask(__name__, template_folder="frontend", static_folder="frontend")
socketio = SocketIO(app)

# Configuration
MODEL_PATH =  r"C:\Users\HP\Desktop\CaptionFlow\vosk-model-en-us-0.22"
SAMPLE_RATE = 16000
BUFFER_SIZE = 4096
MAX_CAPTION_HISTORY = 200  # Keep last 200 captions

# Initialize model with validation
if not os.path.exists(MODEL_PATH):
    raise ValueError(f"Model not found at {MODEL_PATH}. Download from https://alphacephei.com/vosk/models")

model = Model(MODEL_PATH)
captions_log = deque(maxlen=MAX_CAPTION_HISTORY)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/history')
def caption_history():
    return jsonify({'captions': list(captions_log)})

def audio_stream_thread():
    recognizer = KaldiRecognizer(model, SAMPLE_RATE)
    mic = pyaudio.PyAudio()
    
    try:
        stream = mic.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=SAMPLE_RATE,
            input=True,
            frames_per_buffer=BUFFER_SIZE,
            input_device_index=mic.get_default_input_device_info()['index']
        )

        stream.start_stream()
        socketio.emit('status', {'status': 'listening'})

        while True:
            data = stream.read(BUFFER_SIZE, exception_on_overflow=False)
            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                text = result.get('text', '').strip()
                if text:
                    captions_log.append(text)
                    socketio.emit('caption', {'text': text, 'timestamp': time.time()})

    except Exception as e:
        socketio.emit('error', {'message': str(e)})
    finally:
        stream.stop_stream()
        stream.close()
        mic.terminate()

@socketio.on('connect')
def handle_connect():
    socketio.emit('status', {'status': 'connected'})

if __name__ == '__main__':
    socketio.start_background_task(audio_stream_thread)
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, use_reloader=False)