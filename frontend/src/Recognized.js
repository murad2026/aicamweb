import { useState, useEffect } from "react";
import api from "./api";

export default function Recognized({ user }) {
  const [subjects, setSubjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState(null);
  const [editName, setEditName] = useState("");
  const [lightbox, setLightbox] = useState(null);
  const [lightboxIndex, setLightboxIndex] = useState(0);
  const [sightings, setSightings] = useState(null);
  const [sightingsLoading, setSightingsLoading] = useState(false);
  const [sightingPhotos, setSightingPhotos] = useState([]);
  const [sightingIndex, setSightingIndex] = useState(0);

  const plan = user?.plan || "free";

  useEffect(() => {
    if (plan === "premium") {
      api.get("/recognized").then(r => setSubjects(r.data)).finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, [plan]);

  const saveName = async (id) => {
    await api.put(`/subjects/${id}`, { name: editName });
    setSubjects(prev => prev.map(s => s.id === id ? { ...s, name: editName } : s));
    if (sightings?.subject?.id === id) {
      setSightings(prev => ({ ...prev, subject: { ...prev.subject, name: editName } }));
    }
    setEditing(null);
    setEditName("");
  };

  const deleteSubject = async (id) => {
    await api.delete(`/subjects/${id}`);
    setSubjects(prev => prev.filter(s => s.id !== id));
    if (sightings?.subject?.id === id) setSightings(null);
  };

  const openSightings = async (s) => {
    setSightings({ subject: s, list: [] });
    setSightingsLoading(true);
    try {
      const r = await api.get(`/subjects/${s.id}/sightings`);
      setSightings({ subject: s, list: r.data });
    } catch(e) {
      setSightings({ subject: s, list: [] });
    }
    setSightingsLoading(false);
  };

  const openLightbox = (s) => {
    if (!s.photo_url) return;
    window._scrollY = window.scrollY;
    const lbPhotos = subjects.filter(x => x.photo_url);
    const idx = lbPhotos.findIndex(x => x.id === s.id);
    setLightboxIndex(idx >= 0 ? idx : 0);
    setLightbox(s);
  };

  const closeLightbox = () => {
    setLightbox(null);
    setTimeout(() => window.scrollTo(0, window._scrollY || 0), 50);
  };

  const card = {
    background: "#fff", border: "1px solid #e0e0e0",
    borderRadius: 12, overflow: "hidden", display: "flex", flexDirection: "column"
  };
  const input = {
    background: "#f5f5f7", border: "1px solid #ddd", borderRadius: 8,
    padding: "8px 12px", color: "#111", fontSize: 13,
    width: "100%", boxSizing: "border-box", outline: "none"
  };

  const lbPhotos = lightbox?._fromSightings ? sightingPhotos.map(sg => ({ ...sightings?.subject, photo_url: sg.photo_url, _fromSightings: true, _sgId: sg.id })) : subjects.filter(s => s.photo_url);
  const lbIndex = lightbox?._fromSightings ? sightingIndex : lightboxIndex;
  const setLbIndex = lightbox?._fromSightings ? setSightingIndex : setLightboxIndex;

  // Lightbox
  if (lightbox) return (
    <div onClick={closeLightbox} style={{
      position: "fixed", top: 0, left: 0, right: 0, bottom: 0,
      background: "rgba(0,0,0,0.92)", display: "flex", alignItems: "center",
      justifyContent: "center", zIndex: 1100
    }}>
      <div style={{ position: "relative", maxWidth: "80vw", maxHeight: "90vh" }} onClick={e => e.stopPropagation()}>
        <img src={lightbox.photo_url} alt="" style={{
          maxWidth: "80vw", maxHeight: "72vh", objectFit: "contain",
          borderRadius: 8, display: "block", margin: "0 auto"
        }} />
        <div style={{ textAlign: "center", marginTop: 14 }}>
          <p style={{ color: "#fff", fontSize: 18, fontWeight: 700, margin: "0 0 4px" }}>
            {lightbox.name && !lightbox.name.startsWith("Unknown") ? lightbox.name : "Unknown"}
          </p>
          <p style={{ color: "#aaa", fontSize: 13, margin: 0 }}>
            {lightbox.class} · Seen {lightbox.seen_count}x · Last: {lightbox.last_seen?.slice(0, 16)}
          </p>
          <p style={{ color: "#555", fontSize: 12, marginTop: 6 }}>{lbIndex + 1} / {lbPhotos.length}</p>
        </div>
        {/* Close */}
        <button onClick={closeLightbox} style={{
          position: "absolute", top: -44, right: 0, background: "none",
          border: "none", color: "#fff", fontSize: 28, cursor: "pointer", lineHeight: 1
        }}>x</button>
        {/* Prev */}
        {lbIndex > 0 && (
          <button onClick={e => {
            e.stopPropagation();
            const ni = lbIndex - 1;
            setLbIndex(ni);
            setLightbox(lbPhotos[ni]);
          }} style={{
            position: "absolute", left: -68, top: "38%",
            background: "rgba(255,255,255,0.2)", border: "none", color: "#fff",
            fontSize: 30, borderRadius: "50%", width: 54, height: 54,
            cursor: "pointer", display: "flex", alignItems: "center", justifyContent: "center"
          }}>{"<"}</button>
        )}
        {/* Next */}
        {lbIndex < lbPhotos.length - 1 && (
          <button onClick={e => {
            e.stopPropagation();
            const ni = lbIndex + 1;
            setLbIndex(ni);
            setLightbox(lbPhotos[ni]);
          }} style={{
            position: "absolute", right: -68, top: "38%",
            background: "rgba(255,255,255,0.2)", border: "none", color: "#fff",
            fontSize: 30, borderRadius: "50%", width: 54, height: 54,
            cursor: "pointer", display: "flex", alignItems: "center", justifyContent: "center"
          }}>{">"}</button>
        )}
      </div>
    </div>
  );

  // Sightings panel
  if (sightings) {
    const s = sightings.subject;
    return (
      <div style={{ maxWidth: 600 }}>
        <button onClick={() => setSightings(null)} style={{
          background: "none", border: "none", color: "#555", cursor: "pointer", marginBottom: 24, fontSize: 14
        }}>← Back to Recognized</button>
        <div style={{ display: "flex", alignItems: "center", gap: 16, marginBottom: 28 }}>
          {s.photo_url ? (
            <img src={s.photo_url} alt="" style={{ width: 72, height: 72, borderRadius: 12, objectFit: "cover", border: "2px solid #00cc66" }} />
          ) : (
            <div style={{ width: 72, height: 72, borderRadius: 12, background: "#f5f5f7", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 32 }}>👤</div>
          )}
          <div>
            {editing === s.id ? (
              <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
                <input style={{ ...input, width: 160, marginBottom: 0 }} value={editName}
                  onChange={e => setEditName(e.target.value)} autoFocus
                  onKeyDown={e => e.key === "Enter" && saveName(s.id)} placeholder="Enter name" />
                <button onClick={() => saveName(s.id)} style={{ background: "#111", color: "#fff", border: "none", borderRadius: 6, padding: "8px 14px", cursor: "pointer", fontSize: 12 }}>Save</button>
                <button onClick={() => setEditing(null)} style={{ background: "none", border: "1px solid #ddd", borderRadius: 6, padding: "8px 12px", cursor: "pointer", fontSize: 12 }}>Cancel</button>
              </div>
            ) : (
              <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                <h2 style={{ fontSize: 22, fontWeight: 700, color: "#111", margin: 0 }}>
                  {s.name && !s.name.startsWith("Unknown") ? s.name : "Unknown"}
                </h2>
                <button onClick={() => { setEditing(s.id); setEditName(s.name && !s.name.startsWith("Unknown") ? s.name : ""); }} style={{
                  background: "none", border: "1px solid #ddd", borderRadius: 6,
                  padding: "4px 10px", cursor: "pointer", fontSize: 12, color: "#555"
                }}>✏️ Name</button>
              </div>
            )}
            <p style={{ color: "#888", fontSize: 13, margin: "4px 0 0" }}>
              {s.class} · Seen <strong style={{ color: "#00cc66" }}>{s.seen_count}x</strong> · First: {s.first_seen?.slice(0, 10)}
            </p>
          </div>
        </div>
        <h3 style={{ fontSize: 15, fontWeight: 600, color: "#111", marginBottom: 16 }}>Sighting History</h3>
        {sightingsLoading ? (
          <p style={{ color: "#aaa", textAlign: "center", padding: 32 }}>Loading...</p>
        ) : sightings.list.length === 0 ? (
          <p style={{ color: "#aaa", fontSize: 14 }}>No sighting history yet.</p>
        ) : (
          <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
            {sightings.list.map((sg, i) => (
              <div key={sg.id} style={{
                display: "flex", alignItems: "center", gap: 14,
                background: "#fff", border: "1px solid #eee", borderRadius: 10, padding: 12
              }}>
                {sg.photo_url ? (
                  <img src={sg.photo_url} alt=""
                    onClick={() => {
                      const photos = sightings.list.filter(x => x.photo_url);
                      const idx = photos.findIndex(x => x.id === sg.id);
                      setSightingPhotos(photos);
                      setSightingIndex(idx >= 0 ? idx : 0);
                      setLightbox({ ...s, photo_url: photos[idx >= 0 ? idx : 0].photo_url, _fromSightings: true });
                    }}
                    style={{ width: 52, height: 52, borderRadius: 8, objectFit: "cover", cursor: "zoom-in", flexShrink: 0 }} />
                ) : (
                  <div style={{ width: 52, height: 52, borderRadius: 8, background: "#f5f5f7", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 22, flexShrink: 0 }}>👤</div>
                )}
                <div style={{ flex: 1 }}>
                  <div style={{ fontWeight: 600, color: "#111", fontSize: 13, marginBottom: 3 }}>
                    📷 {sg.camera_name || `Camera ${sg.camera_id}`}
                  </div>
                  <div style={{ color: "#888", fontSize: 12 }}>🕐 {sg.timestamp?.slice(0, 16)}</div>
                </div>
                {i === 0 && (
                  <span style={{ background: "#e6fff4", color: "#009950", borderRadius: 20, padding: "3px 10px", fontSize: 11, fontWeight: 600 }}>Latest</span>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    );
  }

  // Upgrade wall
  if (plan !== "premium") return (
    <div style={{ maxWidth: 500, textAlign: "center", paddingTop: 60 }}>
      <div style={{ fontSize: 48, marginBottom: 16 }}>🏷️</div>
      <h2 style={{ fontSize: 22, fontWeight: 700, color: "#111", marginBottom: 12 }}>Recognized Subjects</h2>
      <p style={{ color: "#888", fontSize: 14, lineHeight: 1.6, marginBottom: 24 }}>
        AI automatically recognizes recurring people and objects across cameras. See their full history.
      </p>
      <button style={{
        background: "#00cc66", color: "#fff", border: "none",
        padding: "14px 32px", borderRadius: 8, cursor: "pointer", fontWeight: 600, fontSize: 15, width: "100%"
      }}>Upgrade to Premium — $49/mo</button>
    </div>
  );

  if (loading) return <div style={{ color: "#888", padding: 40, textAlign: "center" }}>Loading...</div>;

  // Main grid
  return (
    <div style={{ maxWidth: 600 }}>
      <h1 style={{ fontFamily: "monospace", fontSize: 28, fontWeight: 700, color: "#111", marginBottom: 8 }}>Recognized</h1>
      <p style={{ color: "#888", fontSize: 14, marginBottom: 24 }}>
        {subjects.length} subject{subjects.length !== 1 ? "s" : ""} the AI has seen more than once
      </p>
      {subjects.length === 0 ? (
        <div style={{ textAlign: "center", padding: 60, border: "2px dashed #e0e0e0", borderRadius: 16 }}>
          <div style={{ fontSize: 48, marginBottom: 16 }}>🔍</div>
          <p style={{ fontSize: 15, color: "#888", marginBottom: 8 }}>No recurring subjects yet</p>
          <p style={{ fontSize: 13, color: "#aaa", lineHeight: 1.6 }}>
            When the AI sees the same person or object more than once,<br />
            they will automatically appear here with their full history.
          </p>
        </div>
      ) : (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(160px, 1fr))", gap: 12 }}>
          {subjects.map(s => (
            <div key={s.id} style={card}>
              <div
                style={{ position: "relative", paddingTop: "100%", background: "#f5f5f7", cursor: s.photo_url ? "pointer" : "default" }}
                onClick={() => openLightbox(s)}
              >
                {s.photo_url ? (
                  <img src={s.photo_url} alt="" style={{
                    position: "absolute", top: 0, left: 0, width: "100%", height: "100%", objectFit: "cover"
                  }} />
                ) : (
                  <div style={{
                    position: "absolute", top: 0, left: 0, width: "100%", height: "100%",
                    display: "flex", alignItems: "center", justifyContent: "center", fontSize: 40
                  }}>👤</div>
                )}
                <div style={{
                  position: "absolute", top: 6, right: 6, background: "#111",
                  color: "#fff", borderRadius: 20, padding: "2px 8px", fontSize: 10
                }}>{s.class}</div>
                <div style={{
                  position: "absolute", top: 6, left: 6, background: "#00cc66",
                  color: "#fff", borderRadius: 20, padding: "2px 8px", fontSize: 10, fontWeight: 700
                }}>x{s.seen_count}</div>
              </div>
              <div style={{ padding: 10 }}>
                {editing === s.id ? (
                  <div>
                    <input style={input} value={editName} onChange={e => setEditName(e.target.value)}
                      placeholder="Enter name" autoFocus onKeyDown={e => e.key === "Enter" && saveName(s.id)} />
                    <div style={{ display: "flex", gap: 6, marginTop: 6 }}>
                      <button onClick={() => saveName(s.id)} style={{ flex: 1, background: "#111", color: "#fff", border: "none", borderRadius: 6, padding: "6px", cursor: "pointer", fontSize: 11 }}>Save</button>
                      <button onClick={() => setEditing(null)} style={{ flex: 1, background: "none", border: "1px solid #ddd", borderRadius: 6, padding: "6px", cursor: "pointer", fontSize: 11 }}>Cancel</button>
                    </div>
                  </div>
                ) : (
                  <div>
                    <div style={{ fontWeight: 700, color: "#111", fontSize: 13, marginBottom: 2 }}>
                      {s.name && !s.name.startsWith("Unknown") ? (
                        <span>⭐ {s.name}</span>
                      ) : (
                        <span style={{ color: "#888" }}>Unknown</span>
                      )}
                    </div>
                    <div style={{ color: "#aaa", fontSize: 10, marginBottom: 6 }}>
                      Last: {s.last_seen?.slice(0, 16)}
                    </div>
                    <div style={{ display: "flex", gap: 5 }}>
                      <button onClick={() => openSightings(s)} style={{
                        flex: 1, background: "#f0f8ff", border: "1px solid #b0d0ff",
                        borderRadius: 6, padding: "5px", cursor: "pointer", fontSize: 10, color: "#2060cc"
                      }}>📋 History</button>
                      <button onClick={() => { setEditing(s.id); setEditName(s.name && !s.name.startsWith("Unknown") ? s.name : ""); }} style={{
                        flex: 1, background: "none", border: "1px solid #ddd",
                        borderRadius: 6, padding: "5px", cursor: "pointer", fontSize: 10, color: "#555"
                      }}>✏️</button>
                      <button onClick={() => deleteSubject(s.id)} style={{
                        background: "none", border: "1px solid #ffcccc",
                        borderRadius: 6, padding: "5px 7px", cursor: "pointer", fontSize: 10, color: "#ff3366"
                      }}>✕</button>
                    </div>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
