from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO
from vosk import Model, KaldiRecognizer
import pyaudio
import json
import os
import time
from threading import Thread
from collections import deque

app = Flask(__name__, template_folder="frontend", static_folder="frontend")
socketio = SocketIO(app, cors_allowed_origins="*")

MODEL_PATH = r"vosk-model-en-us-0.22"
SAMPLE_RATE = 16000
BUFFER_SIZE = 4000
MAX_CAPTION_HISTORY = 200

if not os.path.exists(MODEL_PATH):
    raise ValueError(f"Model not found at {MODEL_PATH}")

model = Model(MODEL_PATH)

is_listening = False
captions_log = deque(maxlen=MAX_CAPTION_HISTORY)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/toggle_mic', methods=['POST'])
def toggle_mic():
    global is_listening
    is_listening = not is_listening
    if is_listening:
        print("Mic turned ON")
    else:
        print("Mic turned OFF")
    return jsonify({'listening': is_listening})

def audio_stream():
    global is_listening
    recognizer = KaldiRecognizer(model, SAMPLE_RATE)
    p = pyaudio.PyAudio()

    try:
        stream = p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=SAMPLE_RATE,
            input=True,
            frames_per_buffer=BUFFER_SIZE
        )

        while True:
            if is_listening:
                data = stream.read(BUFFER_SIZE, exception_on_overflow=False)
                if recognizer.AcceptWaveform(data):
                    result = json.loads(recognizer.Result())
                    text = result.get('text', '').strip()
                    if text:
                        captions_log.append(text)
                        socketio.emit('caption', {'text': text})
                        print(f"Caption: {text}")
            else:
                time.sleep(0.1)

    except Exception as e:
        print(f"Audio Stream Error: {e}")
        socketio.emit('error', {'message': str(e)})

    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()

if __name__ == '__main__':
    Thread(target=audio_stream, daemon=True).start()
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, use_reloader=False)
