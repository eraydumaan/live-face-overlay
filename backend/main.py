import base64
import binascii
from typing import Optional
import logging
import cv2
import numpy as np
from starlette.websockets import WebSocketState
from deepface import DeepFace
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI()

logging.basicConfig(level=logging.INFO)

face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    
)

@app.get("/health")
async def health():
    return {"status": "ok"}

def decode_frame(data: str) -> Optional[np.ndarray]:
    try:
        img_bytes = base64.b64decode(data)
    except binascii.Error:
        return None
    nparr = np.frombuffer(img_bytes, np.uint8)
    return cv2.imdecode(nparr, cv2.IMREAD_COLOR)

def predict_gender(face_bgr: np.ndarray) -> str:
    try:
        face_rgb = cv2.cvtColor(face_bgr, cv2.COLOR_BGR2RGB)
        result = DeepFace.analyze(
            face_rgb,
            actions=["gender"],
            enforce_detection=False,
        )
        if isinstance(result, list):
            result = result[0]
        gender = result.get("dominant_gender", "unknown")
        score = result.get("gender", {}).get(gender, 0)
        return f"{gender} {score:.0f}%"
    except Exception as exc:
        print(f"DeepFace error: {exc}")
        return "unknown"

@app.websocket("/ws")
async def ws_endpoint(ws: WebSocket):
    await ws.accept()
    try:
        while True:
            payload = await ws.receive_text()
            frame = decode_frame(payload)
            if frame is None:
                continue

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.03, minNeighbors=3, minSize=(60,60))
            logging.info("karede %d yüz bulundu", len(faces))

            for (x, y, w, h) in faces:
                face_crop = frame[y : y + h, x : x + w]
                label = predict_gender(face_crop)
                logging.info("tahmin: %s", label)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(
                    frame,
                    label,
                    (x, max(0, y - 10)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 255, 0),
                    2,
                )

            ok, buffer = cv2.imencode(".jpg", frame)
            if not ok:
                continue

            await ws.send_text(base64.b64encode(buffer).decode())
    except WebSocketDisconnect:
        pass
    finally:
        if ws.application_state != WebSocketState.DISCONNECTED:
            await ws.close()
