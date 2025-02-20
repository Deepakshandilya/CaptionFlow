from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO
from vosk import Model, KaldiRecognizer
import pyaudio
import json
import os
import time
from collections import deque
import threading

app = Flask(__name__, template_folder="frontend", static_folder="frontend")
socketio = SocketIO(app, cors_allowed_origins="*")

# Configuration
MODEL_PATH = r"C:\Users\HP\Desktop\CaptionFlow\vosk-model-en-us-0.22"
SAMPLE_RATE = 16000
BUFFER_SIZE = 4096
MAX_CAPTION_HISTORY = 200

# Global states
is_listening = False
captions_log = deque(maxlen=MAX_CAPTION_HISTORY)

if not os.path.exists(MODEL_PATH):
    raise ValueError(f"Model not found at {MODEL_PATH}")

model = Model(MODEL_PATH)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/toggle_mic', methods=['POST'])
def toggle_mic():
    global is_listening
    is_listening = not is_listening
    return jsonify({'listening': is_listening})

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

        while True:
            if is_listening:
                data = stream.read(BUFFER_SIZE, exception_on_overflow=False)
                if recognizer.AcceptWaveform(data):
                    result = json.loads(recognizer.Result())
                    text = result.get('text', '').strip()
                    if text:
                        captions_log.append(text)
                        socketio.emit('caption', {'text': text})
            else:
                time.sleep(0.1)

    except Exception as e:
        socketio.emit('error', {'message': str(e)})
    finally:
        stream.stop_stream()
        stream.close()
        mic.terminate()

if __name__ == '__main__':
    threading.Thread(target=audio_stream_thread, daemon=True).start()
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, use_reloader=False)