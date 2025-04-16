# proctoring/voice_detection.py

import speech_recognition as sr
import time
import threading
from backend import socketio

# Define suspicious keywords
suspicious_keywords = {"cheat", "help", "google", "answer"}

def monitor_voice(user_id):
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    socketio.emit("proctoring_alert", {
        "event": "voice_monitoring",
        "details": f"Voice monitoring started for user {user_id}"
    })

    try:
        with mic as source:
            print("🎤 Calibrating microphone for ambient noise...")
            recognizer.adjust_for_ambient_noise(source)
            print("🎤 Microphone ready")

            start_time = time.time()

            while time.time() - start_time < 30:  # Listen for 30 seconds
                try:
                    print("👂 Listening...")
                    audio = recognizer.listen(source, timeout=5)
                    speech_text = recognizer.recognize_google(audio).lower()
                    print(f"🗣 Recognized: {speech_text}")

                    matched = set(speech_text.split()).intersection(suspicious_keywords)
                    if matched:
                        msg = f"Suspicious words detected: {', '.join(matched)}"
                        socketio.emit("cheating_alert", {
                            "event": "Suspicious Speech",
                            "details": msg,
                            "user_id": user_id
                        })

                    if "exit" in speech_text:
                        break

                except sr.UnknownValueError:
                    print("🤷 Could not understand audio")
                except sr.RequestError as e:
                    print(f"⚠️ Google API error: {e}")
                except Exception as e:
                    print(f"⚠️ Error during recognition: {e}")

    except Exception as e:
        socketio.emit("proctoring_alert", {
            "event": "voice_monitoring_error",
            "details": str(e)
        })

    socketio.emit("proctoring_alert", {
        "event": "voice_monitoring",
        "details": f"Voice monitoring ended for user {user_id}"
    })


# SocketIO trigger
@socketio.on("start_voice_monitoring")
def handle_voice_monitoring(data):
    user_id = data.get("user_id", "unknown")
    threading.Thread(target=monitor_voice, args=(user_id,)).start()

if __name__ == "__main__":
    print("⚙️ Running voice detection manually...")
    monitor_voice("manual_test_user")
