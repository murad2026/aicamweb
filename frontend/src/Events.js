import { useState, useEffect } from "react";
import api from "./api";

export default function Events() {
  const [events, setEvents] = useState([]);

  useEffect(function() {
    api.get("/events").then(function(r) {
      setEvents(r.data);
    });
    const interval = setInterval(function() {
      api.get("/events").then(function(r) {
        setEvents(r.data);
      });
    }, 10000);
    return function() { clearInterval(interval); };
  }, []);

  const icons = { person: "🚶", car: "🚗", motorcycle: "🏍️", cat: "🐱", dog: "🐶", bicycle: "🚲", bus: "🚌", truck: "🚛" };

  return (
    <div>
      <h1 style={{ fontFamily: "monospace", fontSize: 28, fontWeight: 700, color: "#111111", marginBottom: 32 }}>Events</h1>

      {events.length === 0 ? (
        <div style={{ border: "2px dashed #ddd", borderRadius: 12, padding: 80, textAlign: "center", color: "#888" }}>
          <div style={{ fontSize: 48, marginBottom: 16 }}>📋</div>
          <p>No events yet</p>
        </div>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
          {events.map(function(ev) {
            const classes = ev.detected ? ev.detected.split(", ") : [];
            return (
              <div key={ev.id} style={{ background: "#ffffff", border: "1px solid #e0e0e0", borderRadius: 10, padding: "14px 20px", display: "flex", alignItems: "center", gap: 16 }}>
                <div style={{ fontSize: 28 }}>{icons[classes[0]] || "⚠️"}</div>
                <div style={{ flex: 1 }}>
                  <div style={{ display: "flex", gap: 8, alignItems: "center", marginBottom: 4 }}>
                    {classes.map(function(cls) {
                      return <span key={cls} style={{ background: "#e6fff4", color: "#009950", padding: "2px 8px", borderRadius: 20, fontSize: 11 }}>{cls}</span>;
                    })}
                    <span style={{ color: "#888", fontSize: 11 }}>conf: {ev.confidence}</span>
                  </div>
                  <div style={{ color: "#333", fontSize: 12 }}>{ev.camera_name}</div>
                </div>
                <div style={{ fontSize: 11, fontFamily: "monospace", textAlign: "right" }}>
                  <div style={{ color: "#333", marginBottom: 4 }}>
                    {ev.timestamp.split(" ")[1]}<br/>
                    <span style={{ fontSize: 10, color: "#888" }}>{ev.timestamp.split(" ")[0]}</span>
                  </div>
                  {ev.telegram_message_id != null && ev.telegram_message_id !== "null" && (
                    <a href={"https://web.telegram.org/k/#@aianycamera_bot"} target="_blank" rel="noreferrer" style={{
                      background: "#e8f4ff", color: "#2060cc", padding: "3px 8px",
                      borderRadius: 6, fontSize: 11, textDecoration: "none", fontFamily: "sans-serif"
                    }}>✈️ View</a>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
