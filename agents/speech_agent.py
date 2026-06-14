from perception.speech.speech_recognizer import SpeechRecognizer
from perception.speech.command_parser import parse_command

# 🔥 CONFIG
USE_MIC = False   # ← change to True for mic, False for typing

recognizer = SpeechRecognizer("models/vosk-model-small-en-us-0.15")

class SpeechAgent:

    def __init__(self):
        self.last_text = None

    def get_command(self):
        try:
            if USE_MIC:
                text = recognizer.listen_from_mic(duration=4)
            else:
                text = input("🎤 Say command: ")

            if not text or text == self.last_text:
                return {"status": "no_input"}

            self.last_text = text

            command = parse_command(text)

            if not command:
                return {"status": "invalid"}

            return {
                "status": "ok",
                "command": command
            }

        except Exception as e:
            print("❌ Mic Error:", e)
            return {"status": "error"}