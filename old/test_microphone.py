# test_microphone.py
#!/usr/bin/env python3

import argparse
import queue
import sys
import sounddevice as sd
import tkinter as tk
from vosk import Model, KaldiRecognizer
import threading

q = queue.Queue()


def int_or_str(text):
    try:
        return int(text)
    except ValueError:
        return text


def callback(indata, frames, time, status):
    if status:
        print(status, file=sys.stderr)
    q.put(bytes(indata))


def start_recognition(args, text_widget):
    try:
        if args.samplerate is None:
            device_info = sd.query_devices(args.device, "input")
            args.samplerate = int(device_info["default_samplerate"])

        if args.model is None:
            model = Model(lang="en-us")
        else:
            model = Model(lang=args.model)

        with sd.RawInputStream(samplerate=args.samplerate, blocksize=8000, device=args.device,
                               dtype="int16", channels=1, callback=callback):
            rec = KaldiRecognizer(model, args.samplerate)
            while True:
                data = q.get()
                if rec.AcceptWaveform(data):
                    result = rec.Result()
                else:
                    result = rec.PartialResult()
                text_widget.config(state=tk.NORMAL)
                text_widget.insert(tk.END, result + "\n")
                text_widget.see(tk.END)  # Scroll to the end
                text_widget.config(state=tk.DISABLED)
    except Exception as e:
        print(type(e).__name__ + ": " + str(e), file=sys.stderr)


def clear_text(text_widget):
    text_widget.config(state=tk.NORMAL)
    text_widget.delete(1.0, tk.END)
    text_widget.config(state=tk.DISABLED)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--device", type=int_or_str,
                        help="input device (numeric ID or substring)")
    parser.add_argument("-r", "--samplerate", type=int, help="sampling rate")
    parser.add_argument("-m", "--model", type=str,
                        help="language model; e.g., en-us, fr, nl; default is en-us")
    args = parser.parse_args()

    # Set up the tkinter GUI
    root = tk.Tk()
    root.title("Speech-to-Text Transcription")
    text_widget = tk.Text(root, wrap=tk.WORD,
                          state=tk.DISABLED, height=20, width=60)
    text_widget.pack(padx=10, pady=10)

    clear_button = tk.Button(root, text="Clear Text",
                             command=lambda: clear_text(text_widget))
    clear_button.pack(pady=5)

    # Run recognition in a separate thread to avoid blocking the GUI
    recognition_thread = threading.Thread(
        target=start_recognition, args=(args, text_widget), daemon=True)
    recognition_thread.start()

    root.mainloop()


if __name__ == "__main__":
    main()
