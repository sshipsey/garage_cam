import cv2
import mediapipe as mp
from flask import Flask, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import time

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
socketio = SocketIO(app, cors_allowed_origins="*", path="/socket")
cap = cv2.VideoCapture(0)

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False,
                       max_num_hands=2,
                       min_detection_confidence=0.7)

def stream_finger_counts(sid):
    (lastcount := 0)
    while True:
        count = count_fingers()
        if count != lastcount:
          lastcount = count
          socketio.emit("finger_data", {"fingerCount": count}, to=sid)
        time.sleep(1)  # 1 second interval

@socketio.on("connect")
def handle_connect():
    sid = request.sid
    print(f"Client {sid} connected.")
    socketio.start_background_task(stream_finger_counts, sid)

# @app.route("/count", methods=["GET"])

def count_fingers():
    success, frame = cap.read()
    if not success:
        return {"error": "Failed to capture frame"}

    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(image)

    if not results.multi_hand_landmarks or not results.multi_handedness:
        return 0

    finger_data = []

    for i, hand_landmarks in enumerate(results.multi_hand_landmarks):
        handedness = results.multi_handedness[i].classification[0].label  # "Left" or "Right"
        lm = hand_landmarks.landmark

        # Thumb
        if handedness == "Left":
            thumb = 1 if lm[4].x > lm[3].x else 0
        else:  # Right hand
            thumb = 1 if lm[4].x < lm[3].x else 0

        fingers = [thumb]

        # Other 4 fingers
        for tip in [8, 12, 16, 20]:  # index, middle, ring, pinky
            fingers.append(1 if lm[tip].y < lm[tip - 2].y else 0)

        finger_data.append({
            "hand": handedness,
            "fingerCount": sum(fingers),
            "fingers": fingers  # Optional: individual states [1,1,1,1,1]
        })

    total_fingers = sum(hand["fingerCount"] for hand in finger_data)

    return total_fingers
    

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5001)