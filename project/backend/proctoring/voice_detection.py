import speech_recognition as sr
import socketio

# Initialize socket connection
socket = socketio.Client()
try:
    socket.connect("http://localhost:5000")
    print("Socket connected successfully")
except Exception as e:
    print(f"Socket connection failed: {e}")

recognizer = sr.Recognizer()
microphone = sr.Microphone()

# Suspicious keywords to detect
suspicious_keywords = {"cheat", "help", "google"}

with microphone as source:
    print("Calibrating microphone for ambient noise...")
    recognizer.adjust_for_ambient_noise(source)
    print("Microphone ready")

    while True:
        try:
            print("Listening...")
            audio = recognizer.listen(source, timeout=5)
            speech_text = recognizer.recognize_google(audio, language="en-US").lower()
            print(f"Recognized: {speech_text}")

            # Check for suspicious keywords
            matched = set(speech_text.split()).intersection(suspicious_keywords)

            if matched:
                alert_msg = f"Suspicious words detected: {', '.join(matched)}"
                print(alert_msg)
                socket.emit("cheating_alert", {"event": "Suspicious Speech", "details": alert_msg})

            # Exit command
            if "exit" in speech_text:
                print("Exiting monitoring...")
                break

        except sr.UnknownValueError:
            print("Could not understand the audio")
        except sr.RequestError as e:
            print(f"Could not request results; {e}")
        except Exception as e:
            print(f"Error: {e}")
