import json
import queue
import time

import sounddevice as sd
from vosk import KaldiRecognizer, Model

# =============================
# CONFIGURATION
# =============================

MODEL_PATH = "models/vosk-model-small-en-us-0.15"
WAKE_WORD = "hey robot"

COMMANDS = [
    "move left",
    "move right",
    "move up",
    "move down",
    "pick object",
    "drop object",
    "open gripper",
    "close gripper",
    "stop"
]

SAMPLE_RATE = 16000
BLOCK_SIZE = 8000


# =============================
# VOICE AGENT CLASS
# =============================

class VoiceAgent:

    def __init__(self):
        print("Loading Vosk model...")
        self.model = Model(MODEL_PATH)
        self.q = queue.Queue()

    def audio_callback(self, indata, frames, time_info, status):
        if status:
            print(status)
        self.q.put(bytes(indata))

    # -----------------------------
    # 1️⃣ Listen for Wake Word
    # -----------------------------
    def listen_for_wake_word(self):
        print("Listening for wake word...")
        rec = KaldiRecognizer(self.model, SAMPLE_RATE)

        with sd.RawInputStream(
                samplerate=SAMPLE_RATE,
                blocksize=BLOCK_SIZE,
                dtype='int16',
                channels=1,
                callback=self.audio_callback):

            while True:
                data = self.q.get()

                if rec.AcceptWaveform(data):
                    result = json.loads(rec.Result())
                    text = result.get("text", "")

                    if WAKE_WORD in text:
                        print("Wake word detected!")
                        return True

    # -----------------------------
    # 2️⃣ Listen for Restricted Command
    # -----------------------------
    def listen_for_command(self):
        print("Listening for command...")

        grammar = json.dumps(COMMANDS)
        rec = KaldiRecognizer(self.model, SAMPLE_RATE, grammar)

        start_time = time.time()
        timeout = 5  # seconds to wait for command

        with sd.RawInputStream(
                samplerate=SAMPLE_RATE,
                blocksize=BLOCK_SIZE,
                dtype='int16',
                channels=1,
                callback=self.audio_callback):

            while True:
                if time.time() - start_time > timeout:
                    print("Command timeout.")
                    return None

                data = self.q.get()

                if rec.AcceptWaveform(data):
                    result = json.loads(rec.Result())
                    command = result.get("text", "")

                    if command in COMMANDS:
                        print("Command recognized:", command)
                        return command

    # -----------------------------
    # MAIN LOOP
    # -----------------------------
    def run(self):
        while True:
            self.listen_for_wake_word()
            command = self.listen_for_command()

            if command:
                return command


# =============================
# TESTING MODE
# =============================

if __name__ == "__main__":
    agent = VoiceAgent()

    while True:
        command_text = agent.run()
        print("Final Output to Planner:", command_text)
