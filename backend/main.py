import base64
import numpy as np
import cv2
from fastapi import FastAPI, WebSocket,WebSocketDisconnect
app = FastAPI()
@app.get("/health")
async def health():
    return {"status": "ok"}

def decode_frame(data:str):
    try:
        img_bytes = base64.b64decode(data)
    except Exception:
        return None
    nparr = np.frombuffer(img_bytes,np.uint8)
    return cv2.imdecode(nparr,cv2.IMREAD_COLOR)


@app.websocket("/ws")
async def ws_endpoint(ws: WebSocket):
    await ws.accept()
    try:
        while True:
            payload = await ws.receive_text()
            frame = decode_frame(payload)
            if frame is None:
                continue
            ok, buffer = cv2.imencode(".jpg", frame)
            if not ok:
                continue
            await ws.send_text(base64.b64encode(buffer).decode())
    except WebSocketDisconnect:
        pass
    finally:
        await ws.close()
    
