# app.py

import argparse
import queue
import sounddevice as sd
from vosk import Model, KaldiRecognizer
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import threading

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")
q = queue.Queue()


def callback(indata, frames, time, status):
    if status:
        print(status)
    q.put(bytes(indata))


def transcribe_audio(args):
    """Background thread to process audio and emit transcriptions."""
    if args.samplerate is None:
        device_info = sd.query_devices(args.device, "input")
        args.samplerate = int(device_info["default_samplerate"])

    model = Model(lang=args.model if args.model else "en-us")

    with sd.RawInputStream(samplerate=args.samplerate, blocksize=8000, device=args.device,
                           dtype="int16", channels=1, callback=callback):
        recognizer = KaldiRecognizer(model, args.samplerate)
        while True:
            data = q.get()
            if recognizer.AcceptWaveform(data):
                result = recognizer.Result()
                socketio.emit('transcription', result)  # Emit final result
            else:
                result = recognizer.PartialResult()
                socketio.emit('transcription', result)  # Emit partial result


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--device", type=int,
                        help="input device (numeric ID or substring)")
    parser.add_argument("-r", "--samplerate", type=int, help="sampling rate")
    parser.add_argument("-m", "--model", type=str,
                        help="language model; e.g., en-us, fr, nl; default is en-us")
    args = parser.parse_args()

    threading.Thread(target=transcribe_audio,
                     args=(args,), daemon=True).start()
    socketio.run(app, host="0.0.0.0", port=5000)
