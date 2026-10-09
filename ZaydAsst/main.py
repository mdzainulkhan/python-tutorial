import os
import re
import subprocess
import time
import webbrowser
from collections import deque
from datetime import datetime

import numpy as np
import pyttsx3
import sounddevice as sd
import speech_recognition as sr


SAMPLE_RATE = 16000
FRAME_MS = 30
FRAME_SAMPLES = SAMPLE_RATE * FRAME_MS // 1000
CALIBRATION_SECONDS = 0.6
END_SILENCE_SECONDS = 0.7
MAX_PHRASE_SECONDS = 8
COMMAND_TIMEOUT_SECONDS = 8
MIN_VOICE_LEVEL = 250

WAKE_WORDS = ("zayd", "zayad", "zayed", "zade", "zaid", "zayid", "zide")
COMMAND_MARKERS = (
    "youtube", "google", "facebook", "instagram", "gmail", "chatgpt",
    "chrome", "notepad", "calculator", "calc", "file explorer", "explorer",
    "vs code", "visual studio code", "vscode", "time", "date", "stop",
    "exit", "quit", "goodbye", "bye",
)

recognizer = sr.Recognizer()


def speak(engine, text):
    print(f"\n🤖 Zayd: {text}")
    engine.say(text)
    engine.runAndWait()


def rms_level(frame):
    samples = frame.astype(np.float32)
    return float(np.sqrt(np.mean(samples * samples)))


class VoiceListener:
    def __init__(self):
        self.noise_threshold = MIN_VOICE_LEVEL
        self.device = sd.default.device[0]
        sd.check_input_settings(
            device=self.device,
            channels=1,
            dtype="int16",
            samplerate=SAMPLE_RATE,
        )

    def calibrate(self):
        print("🎙️ Calibrating microphone; please stay quiet briefly...")
        levels = []
        frame_count = max(
            1,
            round(CALIBRATION_SECONDS * SAMPLE_RATE / FRAME_SAMPLES),
        )

        with sd.InputStream(
            device=self.device,
            samplerate=SAMPLE_RATE,
            channels=1,
            dtype="int16",
            blocksize=FRAME_SAMPLES,
        ) as stream:
            for _ in range(frame_count):
                frame, overflowed = stream.read(FRAME_SAMPLES)
                if overflowed:
                    print("⚠️ Microphone buffer overflow during calibration.")
                levels.append(rms_level(frame))

        ambient_level = float(np.median(levels))
        self.noise_threshold = max(MIN_VOICE_LEVEL, ambient_level * 2.2)
        print(f"✅ Microphone ready (voice threshold: {self.noise_threshold:.0f}).")

    def listen(self, timeout=None):
        """Capture one speech phrase, ending after a short pause."""
        print("\n🎤 Listening...")
        pre_roll = deque(maxlen=8)
        phrase_frames = []
        silence_frames = 0
        voiced_frames = 0
        onset_frames = 0
        max_frames = round(MAX_PHRASE_SECONDS * 1000 / FRAME_MS)
        silence_limit = round(END_SILENCE_SECONDS * 1000 / FRAME_MS)
        started_waiting = time.monotonic()
        started_speaking = False

        try:
            with sd.InputStream(
                device=self.device,
                samplerate=SAMPLE_RATE,
                channels=1,
                dtype="int16",
                blocksize=FRAME_SAMPLES,
            ) as stream:
                while True:
                    if (
                        timeout is not None
                        and not started_speaking
                        and time.monotonic() - started_waiting >= timeout
                    ):
                        print("⌛ No speech detected before timeout.")
                        return ""

                    frame, overflowed = stream.read(FRAME_SAMPLES)
                    if overflowed:
                        print("⚠️ Microphone buffer overflow; audio may be incomplete.")

                    frame = frame.reshape(-1)
                    is_voice = rms_level(frame) >= self.noise_threshold

                    if not started_speaking:
                        pre_roll.append(frame.copy())
                        onset_frames = onset_frames + 1 if is_voice else 0
                        if onset_frames < 2:
                            continue

                        started_speaking = True
                        phrase_frames.extend(pre_roll)
                        voiced_frames = onset_frames
                        print("🔴 Speech detected.")
                    else:
                        phrase_frames.append(frame.copy())
                        if is_voice:
                            voiced_frames += 1
                            silence_frames = 0
                        else:
                            silence_frames += 1

                    if (
                        started_speaking
                        and (silence_frames >= silence_limit or len(phrase_frames) >= max_frames)
                    ):
                        break
        except sd.PortAudioError as error:
            raise RuntimeError(
                f"Could not read the microphone. Check Windows microphone permissions "
                f"and the selected input device. Details: {error}"
            ) from error

        if voiced_frames < 4:
            print("❌ Speech was too short to recognize.")
            return ""

        audio_bytes = b"".join(frame.tobytes() for frame in phrase_frames)
        audio = sr.AudioData(audio_bytes, SAMPLE_RATE, 2)
        print("🧠 Recognizing speech...")

        try:
            text = recognizer.recognize_google(audio, language="en-IN")
        except sr.UnknownValueError:
            print("❌ I couldn't understand that phrase.")
            return ""
        except sr.RequestError as error:
            print(f"❌ Speech recognition service/network error: {error}")
            return ""

        text = text.lower().strip()
        print(f"👂 Heard: {text}")
        return text


def contains_wake_word(text):
    return any(
        re.search(rf"\b{re.escape(word)}\b", text, re.IGNORECASE)
        for word in WAKE_WORDS
    )


def has_command_marker(text):
    return any(
        re.search(rf"\b{re.escape(marker)}\b", text, re.IGNORECASE)
        for marker in COMMAND_MARKERS
    )


def open_website(engine, url, name):
    opened = webbrowser.open(url, new=2)
    if opened:
        speak(engine, f"Opening {name}")
    else:
        speak(engine, f"I could not open {name}. Please check your default browser.")


def launch_application(engine, name, command):
    try:
        subprocess.Popen(command)
    except OSError as error:
        print(f"❌ Could not launch {name}: {error}")
        speak(engine, f"I could not open {name}.")


def open_application(engine, command):
    if re.search(r"\bchrome\b", command):
        chrome_paths = (
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            os.path.expandvars(
                r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"
            ),
        )
        chrome = next((path for path in chrome_paths if os.path.exists(path)), None)
        if chrome:
            launch_application(engine, "Chrome", [chrome])
        else:
            speak(engine, "I could not find Chrome on this computer.")
        return True

    if re.search(r"\bnotepad\b", command):
        launch_application(engine, "Notepad", ["notepad.exe"])
        return True

    if re.search(r"\b(calculator|calc)\b", command):
        launch_application(engine, "Calculator", ["calc.exe"])
        return True

    if re.search(r"\b(file explorer|explorer)\b", command):
        launch_application(engine, "File Explorer", ["explorer.exe"])
        return True

    if re.search(r"\b(vs code|visual studio code|vscode)\b", command):
        launch_application(engine, "Visual Studio Code", ["code"])
        return True

    return False


def process_command(engine, text):
    command = text.lower().strip()
    print(f"\n⚙️ Processing: {command}")

    if re.search(r"\b(stop|exit|quit|goodbye|bye)\b", command):
        speak(engine, "Goodbye Jainul.")
        return False

    websites = (
        ("youtube", "https://www.youtube.com", "YouTube"),
        ("google", "https://www.google.com", "Google"),
        ("facebook", "https://www.facebook.com", "Facebook"),
        ("instagram", "https://www.instagram.com", "Instagram"),
        ("gmail", "https://mail.google.com", "Gmail"),
        ("chatgpt", "https://chatgpt.com", "ChatGPT"),
    )
    for marker, url, name in websites:
        if re.search(rf"\b{marker}\b", command):
            open_website(engine, url, name)
            return True

    if open_application(engine, command):
        return True

    if re.search(r"\btime\b", command):
        current_time = datetime.now().strftime("%I:%M %p")
        speak(engine, f"The current time is {current_time}")
        return True

    if re.search(r"\bdate\b", command):
        current_date = datetime.now().strftime("%d %B %Y")
        speak(engine, f"Today is {current_date}")
        return True

    speak(engine, "I don't know that command yet.")
    return True


def main():
    engine = pyttsx3.init()
    engine.setProperty("rate", 175)
    engine.setProperty("volume", 1.0)

    listener = VoiceListener()
    listener.calibrate()

    print("\n" + "=" * 55)
    print("                 ZAYD VOICE ASSISTANT")
    print("=" * 55)
    print("Say 'Hi Zayd' to wake me. Speech recognition needs internet.")
    print("Say 'Zayd, open YouTube' to wake and give a command at once.")
    print("Say 'Zayd, stop' to exit.")

    speak(engine, "Hello Jainul. I am Zayd.")

    while True:
        text = listener.listen()
        if not text:
            continue

        if not contains_wake_word(text):
            print("💤 Wake word not detected.")
            continue

        print("🔔 Zayd detected.")
        if has_command_marker(text):
            if process_command(engine, text) is False:
                break
            continue

        speak(engine, "Yes Jainul?")
        command = listener.listen(timeout=COMMAND_TIMEOUT_SECONDS)
        if not command:
            speak(engine, "I didn't hear your command.")
            continue

        if process_command(engine, command) is False:
            break


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Zayd stopped.")
    except (RuntimeError, OSError) as error:
        print(f"\n❌ Zayd could not start or access the microphone: {error}")
