import { useEffect, useState } from "react";

function App() {
  const [logs, setLogs] = useState([]);

  useEffect(() => {
    const ws = new WebSocket("ws://127.0.0.1:8000/ws");
    ws.onopen = () => setLogs(l => [...l, "WS açık"]);
    ws.onmessage = e => setLogs(l => [...l, `Sunucu: ${e.data}`]);
    ws.onerror = err => setLogs(l => [...l, "WS hata: " + err.message]);
    return () => ws.close();
  }, []);

  return (
    <div>
      <h1>WS Test</h1>
      <button
        onClick={() => {
          const ws = new WebSocket("ws://127.0.0.1:8000/ws");
          ws.onopen = () => ws.send("hello");
          ws.onmessage = (e) => {
            alert(e.data);
            ws.close();
          };
        }}
      >
        Mesaj Gönder
      </button>
      <pre>{logs.join("\n")}</pre>
    </div>
  );
}

export default App;
