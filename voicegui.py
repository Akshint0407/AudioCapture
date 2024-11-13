import tkinter as tk
from tkinter import messagebox
import pyaudio
import wave
import threading
import datetime

class VoiceRecorder:
    def __init__(self, root):
        self.root = root
        self.root.title("Voice Recorder")

        self.is_recording = False
        self.p = None  # PyAudio instance
        self.stream = None  # Audio stream

        # GUI Elements
        self.record_button = tk.Button(self.root, text="Start Recording", command=self.toggle_recording, font=("Arial", 12))
        self.record_button.pack(pady=10)

        self.status_label = tk.Label(self.root, text="Status: Not Recording", font=("Arial", 12))
        self.status_label.pack(pady=5)

        tk.Label(self.root, text="Recording Duration (seconds):", font=("Arial", 10)).pack(pady=5)
        self.duration_entry = tk.Entry(self.root, font=("Arial", 10))
        self.duration_entry.pack(pady=5)
        self.duration_entry.insert(0, "5")  # Default duration

    def toggle_recording(self):
        if self.is_recording:
            self.is_recording = False
            self.record_button.config(text="Start Recording")
            self.status_label.config(text="Status: Not Recording")
            self.stop_recording()  # Stop recording properly
        else:
            try:
                self.is_recording = True
                self.record_button.config(text="Stop Recording")
                self.status_label.config(text="Status: Recording...")
                threading.Thread(target=self.record_audio).start()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to start recording: {str(e)}")

    def record_audio(self):
        try:
            # Set up audio recording parameters
            FORMAT = pyaudio.paInt16
            CHANNELS = 1
            RATE = 44100
            CHUNK = 1024
            RECORD_SECONDS = int(self.duration_entry.get())
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            FILE_NAME = f"recording_{timestamp}.wav"

            # Initialize PyAudio and open the stream
            self.p = pyaudio.PyAudio()
            self.stream = self.p.open(format=FORMAT,
                                      channels=CHANNELS,
                                      rate=RATE,
                                      input=True,
                                      frames_per_buffer=CHUNK)

            frames = []
            for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
                if not self.is_recording:
                    break
                data = self.stream.read(CHUNK)
                frames.append(data)

            # Save the recording as a .wav file
            if frames:
                with wave.open(FILE_NAME, 'wb') as wf:
                    wf.setnchannels(CHANNELS)
                    wf.setsampwidth(self.p.get_sample_size(FORMAT))
                    wf.setframerate(RATE)
                    wf.writeframes(b''.join(frames))

                messagebox.showinfo("Recording Saved", f"Recording saved as {FILE_NAME}")
            else:
                messagebox.showinfo("Recording Canceled", "Recording was stopped before any audio was recorded.")

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred during recording: {str(e)}")
        finally:
            self.stop_recording()  # Stop the recording and reset state

    def stop_recording(self):
        """Stop the recording safely."""
        if self.stream is not None:
            self.stream.stop_stream()
            self.stream.close()
        if self.p is not None:
            self.p.terminate()

        self.is_recording = False
        self.record_button.config(text="Start Recording")
        self.status_label.config(text="Status: Not Recording")

if __name__ == "__main__":
    root = tk.Tk()
    app = VoiceRecorder(root)
    root.mainloop()
