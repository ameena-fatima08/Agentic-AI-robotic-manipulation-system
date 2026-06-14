import wave
import json
import time
from vosk import Model, KaldiRecognizer
import pyaudio


class SpeechRecognizer:
    """
    WAV + Microphone based speech recognizer using Vosk.
    """

    def __init__(self, model_path, sample_rate=16000):
        print("Loading Vosk model...")
        self.model = Model(model_path)
        self.sample_rate = sample_rate

    # ---------------------------------
    # WAV FILE INPUT
    # ---------------------------------
    def listen(self, wav_path, grammar=None, timeout=None):

        wf = wave.open(wav_path, "rb")

        if wf.getnchannels() != 1 or wf.getsampwidth() != 2:
            raise ValueError("WAV must be mono 16-bit PCM")

        rec = KaldiRecognizer(self.model, wf.getframerate())

        if grammar:
            rec = KaldiRecognizer(self.model, wf.getframerate(), grammar)

        result_text = ""

        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break

            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                result_text += " " + result.get("text", "")

        final_result = json.loads(rec.FinalResult())
        result_text += " " + final_result.get("text", "")

        text = result_text.strip()
        print("Recognized:", text)

        return text if text else None

    # ---------------------------------
    # MICROPHONE INPUT
    # ---------------------------------
    def listen_from_mic(self, duration=5, grammar=None):

        print("🎤 Listening from microphone...")

        p = pyaudio.PyAudio()

        stream = p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self.sample_rate,
            input=True,
            frames_per_buffer=4000
        )

        rec = KaldiRecognizer(self.model, self.sample_rate)

        if grammar:
            rec = KaldiRecognizer(self.model, self.sample_rate, grammar)

        start_time = time.time()
        result_text = ""

        while True:
            data = stream.read(4000, exception_on_overflow=False)

            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                result_text += " " + result.get("text", "")

            # ⏱️ stop after duration
            if time.time() - start_time > duration:
                break

        final_result = json.loads(rec.FinalResult())
        result_text += " " + final_result.get("text", "")

        stream.stop_stream()
        stream.close()
        p.terminate()

        text = result_text.strip()
        print("Recognized:", text)

        return text if text else None