import { useEffect, useRef } from "react";

const WIDTH = 640;
const HEIGHT = 480;

function App() {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const wsRef = useRef(null);
  const timerRef = useRef(null);

  useEffect(() => {
    navigator.mediaDevices.getUserMedia({ video: true })
      .then(stream => {
        if (videoRef.current) videoRef.current.srcObject = stream;
      })
      .catch(err => console.error("Kamera:", err));

    const ws = new WebSocket("ws://127.0.0.1:8000/ws");
    wsRef.current = ws;

    ws.onmessage = evt => {
      const img = new Image();
      img.onload = () => {
        const ctx = canvasRef.current?.getContext("2d");
        if (ctx) ctx.drawImage(img, 0, 0, WIDTH, HEIGHT);
      };
      img.src = "data:image/jpeg;base64," + evt.data;
    };

    ws.onopen = () => startSendingFrames();

    return () => {
      stopSendingFrames();
      ws.close();
      const tracks = videoRef.current?.srcObject?.getTracks();
      tracks?.forEach(t => t.stop());
    };
  }, []);

  const startSendingFrames = () => {
    const send = () => {
      const video = videoRef.current;
      const ws = wsRef.current;
      if (!video || ws?.readyState !== WebSocket.OPEN) return;

      const canvas = document.createElement("canvas");
      canvas.width = WIDTH;
      canvas.height = HEIGHT;
      const ctx = canvas.getContext("2d");
      ctx.drawImage(video, 0, 0, WIDTH, HEIGHT);
      const data = canvas.toDataURL("image/jpeg");
      ws.send(data.split(",")[1]);

      timerRef.current = setTimeout(send, 200);
    };
    send();
  };

  const stopSendingFrames = () => {
    if (timerRef.current) {
      clearTimeout(timerRef.current);
      timerRef.current = null;
    }
  };

  return (
    <div>
      <video ref={videoRef} width={WIDTH} height={HEIGHT} autoPlay muted playsInline />
      <canvas ref={canvasRef} width={WIDTH} height={HEIGHT} />
    </div>
  );
}

export default App;
