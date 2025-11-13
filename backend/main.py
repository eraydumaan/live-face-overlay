from fastapi import FastAPI
from fastapi import WebSocket
app = FastAPI()
@app.get("/health")
async def health():
    return {"status": "ok"}

@app.websocket("/ws")
async def ws_endpoint(ws: WebSocket):
    await ws.accept()
    try:
        while True:
            message = await ws.receive_text()
            await ws.send_text(f"echo: {message}")
    except Exception:
        await ws.close()
    
    