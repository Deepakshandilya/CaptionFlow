# CaptionFlow - Real-time Voice Captions

CaptionFlow is a real-time speech-to-text application that transcribes spoken audio into live captions using the Vosk speech recognition engine and Flask-SocketIO.

## Features
- Real-time voice recognition captions
- Interactive frontend with mic control button
- Backend using Flask, Flask-SocketIO, and Vosk
- Supports live audio input via microphone
- Caption history available via REST endpoint

---

## Prerequisites
Make sure you have the following installed:
- Python 3.8 or higher
- Visual Studio Code (VSCode)
- Pip

---

## Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/Deepakshandilya/CaptionFlow.git
cd CaptionFlow
```

### 2. Create a Virtual Environment
```bash
python -m venv venv
```

### 3. Activate Virtual Environment
#### On Windows:
```bash
venv\Scripts\activate
```
#### On macOS/Linux:
```bash
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Download Vosk Model
Download the Vosk model from [https://alphacephei.com/vosk/models](https://alphacephei.com/vosk/models) and extract it to the `models/` folder. Example structure:
```
models/
    vosk-model-en-us-0.42/
```

### 6. Run the Application
```bash
python app.py
```
The server will start on `http://127.0.0.1:5000`

---

## How the Project Works
1. **Frontend (HTML + TailwindCSS + SocketIO):**
    - Renders a live caption interface.
    - Has a mic button to control the microphone.
    - Uses WebSocket (Socket.IO) to receive live captions from the backend.

2. **Backend (Flask + Flask-SocketIO + Vosk):**
    - Loads the Vosk speech recognition model.
    - Captures audio using PyAudio and processes it using Vosk.
    - Sends recognized text as captions via WebSocket in real-time.
    - Provides caption history via `/history` endpoint.

---

## Useful Commands
- **Deactivate Virtual Environment:**
  ```bash
  deactivate
  ```

---

## Running in VSCode
1. Open the folder containing the project in VSCode.
2. Open a new terminal in VSCode.
3. Activate the virtual environment:
    - Windows: `venv\Scripts\activate`
    - macOS/Linux: `source venv/bin/activate`
4. Run the app using `python app.py`.
5. Open `http://127.0.0.1:5000` in your browser.

---

