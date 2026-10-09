import sounddevice as sd
import speech_recognition as sr

SAMPLE_RATE = 16000
CHANNELS = 1
RECORD_SECONDS = 5

print("========================================")
print("       ZAYD VOICE TEST")
print("========================================")

print("\n🎤 Speak clearly after this message.")
print("Say: OPEN YOUTUBE")

input("\nPress ENTER when ready...")

print("\n🎤 Recording...")

audio = sd.rec(
    int(RECORD_SECONDS * SAMPLE_RATE),
    samplerate=SAMPLE_RATE,
    channels=CHANNELS,
    dtype="int16"
)

sd.wait()

print("🔄 Recording finished.")
print("🧠 Sending audio for recognition...")

recognizer = sr.Recognizer()

audio_data = sr.AudioData(
    audio.tobytes(),
    SAMPLE_RATE,
    2
)

try:

    text = recognizer.recognize_google(
        audio_data,
        language="en-IN"
    )

    print("\n========================================")
    print("✅ RECOGNIZED:")
    print(text)
    print("========================================")

except sr.UnknownValueError:

    print("\n❌ Google could not understand the audio.")

except sr.RequestError as error:

    print("\n❌ Google Speech API error:")
    print(error)

except Exception as error:

    print("\n❌ ERROR:")
    print(error)