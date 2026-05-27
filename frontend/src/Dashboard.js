import { useState, useEffect, useCallback } from "react";
import api from "./api";
import ZoneEditor from "./ZoneEditor";

export default function Dashboard({ onAdd }) {
  const [cameras, setCameras] = useState([]);
  const [snapshot, setSnapshot] = useState(null);
  const [snapLoading, setSnapLoading] = useState(false);
  const [events, setEvents] = useState(null);
  const [editingZone, setEditingZone] = useState(null);

  const viewCamera = function(cam) {
    setSnapshot({ cam: cam, image: null });
    setSnapLoading(true);
    api.get("/cameras/" + cam.id + "/snapshot").then(function(r) {
      setSnapshot({ cam: cam, image: r.data.image });
      setSnapLoading(false);
    }).catch(function() {
      setSnapLoading(false);
    });
  };

  const viewEvents = async function(cam) {
    const r = await api.get("/events/" + cam.id);
    setEvents({ cam, list: r.data });
  };

  const deleteEvent = async function(eventId, cam) {
    await api.delete("/events/" + eventId);
    viewEvents(cam);
  };

  const deleteAllEvents = async function(cam) {
    await api.delete("/events/camera/" + cam.id);
    setEvents(null);
  };

  const loadCameras = useCallback(function() {
    api.get("/cameras").then(function(r) {
      api.get("/status").then(function(s) {
        const status = s.data;
        const camsWithStatus = r.data.map(function(cam) {
          const st = status[String(cam.id)];
          return Object.assign({}, cam, {
            _running: st ? st.running : false,
            _connected: st ? st.connected : false,
            _present: st ? st.present : false,
            _error: st ? st.error : null
          });
        });
        setCameras(camsWithStatus);
      }).catch(function() { setCameras(r.data); });
    });
  }, []);

  useEffect(function() {
    loadCameras();
    const interval = setInterval(loadCameras, 10000);
    return function() { clearInterval(interval); };
  }, [loadCameras]);

  const [eventCounts, setEventCounts] = useState({});
  useEffect(function() {
    cameras.forEach(function(cam) {
      api.get("/events/" + cam.id).then(function(r) {
        setEventCounts(function(prev) { return Object.assign({}, prev, { [cam.id]: r.data.length }); });
      }).catch(function() {});
    });
  }, [cameras]);

  if (editingZone) {
    return <ZoneEditor camera={editingZone} onBack={function() { setEditingZone(null); loadCameras(); }} />;
  }

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 32 }}>
        <h1 style={{ fontFamily: "monospace", fontSize: 28, fontWeight: 700, color: "#111" }}>Your Cameras</h1>
        <button onClick={onAdd} style={{ background: "#00cc66", color: "#fff", border: "none", padding: "10px 24px", borderRadius: 8, cursor: "pointer", fontWeight: 600 }}>+ Add Camera</button>
      </div>

      {cameras.length === 0 ? (
        <div style={{ border: "2px dashed #e0e0e0", borderRadius: 12, padding: 80, textAlign: "center", color: "#888" }}>
          <div style={{ fontSize: 48, marginBottom: 16 }}>⬡</div>
          <p style={{ marginBottom: 24 }}>No cameras yet</p>
          <button onClick={onAdd} style={{ background: "#00cc66", color: "#fff", border: "none", padding: "12px 28px", borderRadius: 8, cursor: "pointer", fontWeight: 600 }}>Add your first camera</button>
        </div>
      ) : (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(min(300px, 100%), 1fr))", gap: 16, alignItems: "stretch" }}>
          {cameras.map(function(cam) {
            const evCount = cam.total_events || eventCounts[cam.id] || 0;
            const newEvCount = cam.new_events || 0;
            return (
              <div key={cam.id} style={{
                background: "#ffffff", border: "1px solid #e0e0e0", borderRadius: 12, padding: 24,
                boxShadow: "0 1px 4px rgba(0,0,0,0.06)",
                display: "flex", flexDirection: "column"
              }}>
                <div style={{ flex: 1 }}>
                  <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 12 }}>
                    <div>
                      <h3 style={{ color: "#111", fontSize: 18, marginBottom: 4 }}>{cam.name}</h3>
                      <span style={{ color: "#00cc66", fontSize: 12, fontFamily: "monospace" }}>{cam.brand}</span>
                    </div>
                    <span style={{
                      color: cam._present ? "#e65c00" : cam._error ? "#ff3366" : cam._connected ? "#009950" : cam._running ? "#f0a500" : "#aaa",
                      fontSize: 12, fontWeight: 700
                    }}>
                      {cam._present ? "● MOTION" : cam._error ? "● ERROR" : cam._connected ? "● ACTIVE" : cam._running ? "● CONNECTING..." : "● OFFLINE"}
                    </span>
                  </div>
                  <div style={{ display: "flex", flexWrap: "wrap", gap: 6, marginBottom: 12 }}>
                    {cam.detect_classes && cam.detect_classes.map(function(cls) {
                      return <span key={cls} style={{ background: "#f0f0f0", color: "#555", padding: "3px 10px", borderRadius: 20, fontSize: 11 }}>{cls}</span>;
                    })}
                  </div>
                  <div style={{ display: "flex", gap: 8, marginBottom: 16 }}>
                    {cam.notify_telegram
                      ? <span style={{ background: "#e8f0ff", color: "#2060cc", padding: "3px 10px", borderRadius: 20, fontSize: 11 }}>✈️ {cam.notify_telegram}</span>
                      : <span style={{ color: "#bbb", fontSize: 11 }}>No alerts configured</span>
                    }
                  </div>
                </div>

                <div>
                  <button onClick={function() { setEditingZone(cam); }} style={{
                    background: cam.zone ? "#e6fff4" : "#f5f5f5",
                    border: cam.zone ? "1px solid #00c96e" : "1px solid #ddd",
                    color: cam.zone ? "#009950" : "#666",
                    padding: "8px 16px", borderRadius: 8, cursor: "pointer", fontSize: 12, width: "100%", marginBottom: 8
                  }}>
                    {cam.zone ? "✓ Zone configured — Edit" : "Draw Alert Zone"}
                  </button>
                  <button onClick={function() { viewCamera(cam); }} style={{
                    background: "#f0f8ff", border: "1px solid #b0d0ff", color: "#2060cc",
                    padding: "8px", borderRadius: 8, cursor: "pointer", fontSize: 13,
                    fontWeight: 500, width: "100%", marginBottom: 8
                  }}>📷 View Camera</button>

                  {evCount > 0 && (
                    <button onClick={function() {
                      viewEvents(cam);
                      // Mark as viewed
                      api.post("/events/" + cam.id + "/mark-viewed").catch(() => {});
                    }} style={{
                      background: newEvCount > 0 ? "#f0f5ff" : "#fff8e6",
                      border: newEvCount > 0 ? "1px solid #3366ff" : "1px solid #ffcc66",
                      color: newEvCount > 0 ? "#0033cc" : "#cc8800",
                      padding: "8px", borderRadius: 8, cursor: "pointer", fontSize: 13,
                      fontWeight: 500, width: "100%", marginBottom: 8,
                      display: "flex", alignItems: "center", justifyContent: "center", gap: 6
                    }}>
                      {newEvCount > 0 ? "🔵" : "🔔"} Events ({evCount}){newEvCount > 0 && <span style={{ background: "#3366ff", color: "#fff", borderRadius: 20, padding: "1px 7px", fontSize: 11, fontWeight: 700 }}>{newEvCount} new</span>}
                    </button>
                  )}

                  {cam._confirmDelete ? (
                    <div style={{ display: "flex", gap: 8 }}>
                      <button onClick={function() { api.delete("/cameras/" + cam.id).then(loadCameras); }} style={{ flex: 1, background: "#ff3366", border: "none", color: "#fff", padding: "8px", borderRadius: 8, cursor: "pointer", fontSize: 12, fontWeight: 600 }}>Confirm Delete</button>
                      <button onClick={function() { setCameras(function(prev) { return prev.map(function(c) { return c.id === cam.id ? Object.assign({}, c, {_confirmDelete: false}) : c; }); }); }} style={{ flex: 1, background: "none", border: "1px solid #ddd", color: "#666", padding: "8px", borderRadius: 8, cursor: "pointer", fontSize: 12 }}>Cancel</button>
                    </div>
                  ) : (
                    <button onClick={function() { setCameras(function(prev) { return prev.map(function(c) { return c.id === cam.id ? Object.assign({}, c, {_confirmDelete: true}) : c; }); }); }} style={{
                      background: "none", border: "1px solid #e0e0e0", color: "#999",
                      padding: "8px 16px", borderRadius: 8, cursor: "pointer", fontSize: 12, width: "100%"
                    }}>🗑 Delete Camera</button>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Events Modal */}
      {events && (
        <div onClick={function() { setEvents(null); }} style={{
          position: "fixed", top: 0, left: 0, right: 0, bottom: 0,
          background: "rgba(0,0,0,0.7)", zIndex: 1000,
          display: "flex", alignItems: "center", justifyContent: "center", padding: 16
        }}>
          <div onClick={function(e) { e.stopPropagation(); }} style={{
            background: "#fff", borderRadius: 12, width: "100%", maxWidth: 600, maxHeight: "80vh", display: "flex", flexDirection: "column"
          }}>
            <div style={{ padding: "16px 20px", borderBottom: "1px solid #f0f0f0", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <span style={{ fontWeight: 600, color: "#111" }}>🔔 {events.cam.name} Events</span>
              <div style={{ display: "flex", gap: 8 }}>
                <button onClick={function() { deleteAllEvents(events.cam); }} style={{ background: "#fff0f0", border: "1px solid #ffcccc", color: "#cc0000", padding: "6px 12px", borderRadius: 6, cursor: "pointer", fontSize: 12 }}>Delete All</button>
                <button onClick={function() { setEvents(null); }} style={{ background: "none", border: "none", color: "#aaa", fontSize: 20, cursor: "pointer" }}>✕</button>
              </div>
            </div>
            <div style={{ overflowY: "auto", flex: 1 }}>
              {events.list.length === 0 ? (
                <div style={{ padding: 40, textAlign: "center", color: "#999" }}>No events</div>
              ) : events.list.map(function(ev) {
                return (
                  <div key={ev.id} style={{ padding: "14px 20px", borderBottom: "1px solid #f5f5f5", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                    <div>
                      <div style={{ fontWeight: 500, color: "#111", fontSize: 14 }}>🚨 {ev.detected}</div>
                      {ev.photo_url && <a href={ev.photo_url} target="_blank" rel="noreferrer"><img src={ev.photo_url} alt="snapshot" style={{ width: "100%", borderRadius: 8, marginTop: 8 }} /></a>}
                      <div style={{ color: "#aaa", fontSize: 12, marginTop: 4 }}>{ev.timestamp} · conf: {ev.confidence}</div>
                    </div>
                    <button onClick={function() { deleteEvent(ev.id, events.cam); }} style={{ background: "none", border: "1px solid #eee", color: "#ccc", padding: "4px 10px", borderRadius: 6, cursor: "pointer", fontSize: 12 }}>✕</button>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}

      {/* Snapshot Modal */}
      {snapshot && (
        <div onClick={function() { setSnapshot(null); }} style={{
          position: "fixed", top: 0, left: 0, right: 0, bottom: 0,
          background: "rgba(0,0,0,0.85)", zIndex: 1000,
          display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", padding: 16
        }}>
          <div onClick={function(e) { e.stopPropagation(); }} style={{
            background: "#fff", borderRadius: 12, overflow: "hidden", width: "100%", maxWidth: 800, maxHeight: "90vh"
          }}>
            <div style={{ padding: "12px 16px", display: "flex", justifyContent: "space-between", alignItems: "center", borderBottom: "1px solid #f0f0f0" }}>
              <span style={{ color: "#111", fontWeight: 600 }}>📷 {snapshot.cam.name}</span>
              <button onClick={function() { setSnapshot(null); viewCamera(snapshot.cam); }} style={{ background: "none", border: "1px solid #e0e0e0", color: "#888", padding: "4px 10px", borderRadius: 6, cursor: "pointer", fontSize: 12, marginRight: 8 }}>🔄 Refresh</button>
              <button onClick={function() { setSnapshot(null); }} style={{ background: "none", border: "none", color: "#aaa", fontSize: 20, cursor: "pointer" }}>✕</button>
            </div>
            {snapLoading ? (
              <div style={{ padding: 60, textAlign: "center" }}>
                <div style={{ width: 40, height: 40, border: "3px solid #f0f0f0", borderTop: "3px solid #00cc66", borderRadius: "50%", animation: "spin 0.8s linear infinite", margin: "0 auto 16px" }} />
                <p style={{ color: "#00cc66" }}>Loading...</p>
                <style>{"@keyframes spin { to { transform: rotate(360deg); } }"}</style>
              </div>
            ) : snapshot.image ? (
              <img src={snapshot.image} alt="camera" style={{ width: "100%", display: "block" }} />
            ) : (
              <div style={{ padding: 40, textAlign: "center", color: "#999" }}>Could not load snapshot</div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
