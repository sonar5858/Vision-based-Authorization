import face_recognition
import cv2
import os
import paho.mqtt.client as mqtt

# MQTT Setup
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "plc/batch_control"
client = mqtt.Client()
client.connect(MQTT_BROKER, MQTT_PORT, 60)

# Load known faces
known_face_encodings = []
known_face_names = []

known_dir = "known_faces"
for filename in os.listdir(known_dir):
    if filename.endswith(".jpg") or filename.endswith(".png"):
        image_path = os.path.join(known_dir, filename)
        image = face_recognition.load_image_file(image_path)
        print(f"Loaded {filename} with shape: {image.shape} and dtype: {image.dtype}")

        encodings = face_recognition.face_encodings(image)
        if encodings:
            known_face_encodings.append(encodings[0])
            known_face_names.append(os.path.splitext(filename)[0])

# Webcam feed
video_capture = cv2.VideoCapture(0)
print("🔍 Face recognition started...")

while True:
    ret, frame = video_capture.read()
    if not ret:
        continue

    rgb_frame = frame[:, :, ::-1]  # BGR to RGB
    face_locations = face_recognition.face_locations(rgb_frame)
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

    for face_encoding in face_encodings:
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
        name = "Not Authorized"

        if True in matches:
            match_index = matches.index(True)
            name = known_face_names[match_index]
            client.publish(MQTT_TOPIC, "ALLOW_START = True")
            print(f"✅ Authorized: {name} — MQTT signal sent")

        else:
            print("❌ Not Authorized — unknown face detected")

    cv2.imshow("Touchless Batch Start", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

video_capture.release()
cv2.destroyAllWindows()
