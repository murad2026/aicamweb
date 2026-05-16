import { useState, useEffect } from "react";
import api from "./api";

export default function Events() {
  const [events, setEvents] = useState([]);

  useEffect(function() {
    api.get("https://b48a-108-26-229-43.ngrok-free.app/events").then(function(r) {
      setEvents(r.data);
    });
    const interval = setInterval(function() {
      api.get("https://b48a-108-26-229-43.ngrok-free.app/events").then(function(r) {
        setEvents(r.data);
      });
    }, 10000);
    return function() { clearInterval(interval); };
  }, []);

  const icons = { person: "🚶", car: "🚗", motorcycle: "🏍️", cat: "🐱", dog: "🐶", bicycle: "🚲", bus: "🚌", truck: "🚛" };

  return (
    <div>
      <h1 style={{ fontFamily: "monospace", fontSize: 28, fontWeight: 700, color: "#f0f0f0", marginBottom: 32 }}>Events</h1>

      {events.length === 0 ? (
        <div style={{ border: "1px dashed #333", borderRadius: 12, padding: 80, textAlign: "center", color: "#444" }}>
          <div style={{ fontSize: 48, marginBottom: 16 }}>📋</div>
          <p>No events yet</p>
        </div>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
          {events.map(function(ev) {
            const classes = ev.detected ? ev.detected.split(", ") : [];
            return (
              <div key={ev.id} style={{ background: "#111", border: "1px solid #222", borderRadius: 10, padding: "14px 20px", display: "flex", alignItems: "center", gap: 16 }}>
                <div style={{ fontSize: 28 }}>{icons[classes[0]] || "⚠️"}</div>
                <div style={{ flex: 1 }}>
                  <div style={{ display: "flex", gap: 8, alignItems: "center", marginBottom: 4 }}>
                    {classes.map(function(cls) {
                      return <span key={cls} style={{ background: "#001a0d", color: "#00ff88", padding: "2px 8px", borderRadius: 20, fontSize: 11 }}>{cls}</span>;
                    })}
                    <span style={{ color: "#444", fontSize: 11 }}>conf: {ev.confidence}</span>
                  </div>
                  <div style={{ color: "#555", fontSize: 12 }}>{ev.camera_name}</div>
                </div>
                <div style={{ color: "#333", fontSize: 11, fontFamily: "monospace", textAlign: "right" }}>
                  {ev.timestamp.split(" ")[1]}<br/>
                  <span style={{ fontSize: 10 }}>{ev.timestamp.split(" ")[0]}</span>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
