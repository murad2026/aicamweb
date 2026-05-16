import { useState, useEffect, useCallback } from "react";
import api from "./api";
import ZoneEditor from "./ZoneEditor";

export default function Dashboard({ onAdd }) {
  const [cameras, setCameras] = useState([]);
  const [editingZone, setEditingZone] = useState(null);

  const loadCameras = useCallback(function() {
    api.get("https://b48a-108-26-229-43.ngrok-free.app/cameras").then(function(r) {
      setCameras(r.data);
    });
  }, []);

  useEffect(function() {
    loadCameras();
  }, [loadCameras]);

  const handleBackFromZone = function() {
    setEditingZone(null);
    loadCameras();
  };

  if (editingZone) {
    return <ZoneEditor camera={editingZone} onBack={handleBackFromZone} />;
  }

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 32 }}>
        <h1 style={{ fontFamily: "monospace", fontSize: 28, fontWeight: 700, color: "#f0f0f0" }}>Your Cameras</h1>
        <button onClick={onAdd} style={{ background: "#00ff88", color: "#000", border: "none", padding: "10px 24px", borderRadius: 8, cursor: "pointer", fontWeight: 500 }}>+ Add Camera</button>
      </div>

      {cameras.length === 0 ? (
        <div style={{ border: "1px dashed #333", borderRadius: 12, padding: 80, textAlign: "center", color: "#444" }}>
          <div style={{ fontSize: 48, marginBottom: 16 }}>⬡</div>
          <p style={{ marginBottom: 24 }}>No cameras yet</p>
          <button onClick={onAdd} style={{ background: "#00ff88", color: "#000", border: "none", padding: "12px 28px", borderRadius: 8, cursor: "pointer", fontWeight: 500 }}>Add your first camera</button>
        </div>
      ) : (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(min(300px, 100%), 1fr))", gap: 16 }}>
          {cameras.map(function(cam) {
            return (
              <div key={cam.id} style={{ background: "#111", border: "1px solid #222", borderRadius: 12, padding: 24 }}>
                <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 12 }}>
                  <div>
                    <h3 style={{ color: "#f0f0f0", fontSize: 18, marginBottom: 4 }}>{cam.name}</h3>
                    <span style={{ color: "#00ff88", fontSize: 12, fontFamily: "monospace" }}>{cam.brand}</span>
                  </div>
                  <span style={{ background: "#001a0d", color: "#00ff88", padding: "4px 10px", borderRadius: 20, fontSize: 11 }}>● ACTIVE</span>
                </div>
                <p style={{ color: "#444", fontSize: 11, fontFamily: "monospace", marginBottom: 16, wordBreak: "break-all" }}>{cam.rtsp_url}</p>
                <div style={{ display: "flex", flexWrap: "wrap", gap: 6, marginBottom: 12 }}>
                  {cam.detect_classes && cam.detect_classes.map(function(cls) {
                    return <span key={cls} style={{ background: "#1a1a1a", color: "#666", padding: "3px 10px", borderRadius: 20, fontSize: 11 }}>{cls}</span>;
                  })}
                </div>
                <div style={{ display: "flex", gap: 8, marginBottom: 16 }}>
                  {cam.notify_telegram
                    ? <span style={{ background: "#001a2a", color: "#0099ff", padding: "3px 10px", borderRadius: 20, fontSize: 11 }}>✈️ {cam.notify_telegram}</span>
                    : <span style={{ color: "#333", fontSize: 11 }}>No alerts configured</span>
                  }
                </div>
                <button onClick={function() { setEditingZone(cam); }} style={{
                  background: cam.zone ? "#001a0d" : "none",
                  border: cam.zone ? "1px solid #00ff88" : "1px solid #333",
                  color: cam.zone ? "#00ff88" : "#555",
                  padding: "8px 16px", borderRadius: 8, cursor: "pointer", fontSize: 12, width: "100%",
                  marginBottom: 8
                }}>
                  {cam.zone ? "✓ Zone configured — Edit" : "Draw Alert Zone"}
                </button>
                <button onClick={function() {
                  if (window.confirm("Delete camera " + cam.name + "?")) {
                    api.delete("https://b48a-108-26-229-43.ngrok-free.app/cameras/" + cam.id).then(loadCameras);
                  }
                }} style={{
                  background: "none", border: "1px solid #333", color: "#666",
                  padding: "8px 16px", borderRadius: 8, cursor: "pointer", fontSize: 12, width: "100%"
                }}
                onMouseEnter={function(e) { e.currentTarget.style.borderColor = "#ff3366"; e.currentTarget.style.color = "#ff3366"; }}
                onMouseLeave={function(e) { e.currentTarget.style.borderColor = "#333"; e.currentTarget.style.color = "#666"; }}
                >🗑 Delete Camera</button>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
