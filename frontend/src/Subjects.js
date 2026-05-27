import { useState, useEffect } from "react";
import api from "./api";

export default function Subjects({ user }) {
  const [subjects, setSubjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState(null);
  const [lightbox, setLightbox] = useState(null);
  const [editName, setEditName] = useState("");

  const plan = user?.plan || "free";

  useEffect(() => {
    if (plan === "premium") {
      api.get("/subjects").then(r => setSubjects(r.data)).finally(() => setLoading(false));
      // Mark all as viewed
      api.post("/subjects/mark-viewed").catch(() => {});
    } else {
      setLoading(false);
    }
  }, [plan]);

  const saveName = async (id) => {
    await api.put(`/subjects/${id}`, { name: editName });
    setSubjects(subjects.map(s => s.id === id ? { ...s, name: editName } : s));
    setEditing(null);
    setEditName("");
  };

  const deleteSubject = async (id) => {
    await api.delete(`/subjects/${id}`);
    setSubjects(subjects.filter(s => s.id !== id));
  };

  const card = { background: "#fff", border: "1px solid #e0e0e0", borderRadius: 12, overflow: "hidden", display: "flex", flexDirection: "column" };
  const input = { background: "#f5f5f7", border: "1px solid #ddd", borderRadius: 8, padding: "8px 12px", color: "#111", fontSize: 13, width: "100%", boxSizing: "border-box", outline: "none" };

  if (lightbox) return (
    <div onClick={() => { setLightbox(null); setTimeout(() => window.scrollTo(0, window._scrollY || 0), 50); }} style={{ position: "fixed", top: 0, left: 0, right: 0, bottom: 0, background: "rgba(0,0,0,0.9)", display: "flex", alignItems: "center", justifyContent: "center", zIndex: 1000, cursor: "zoom-out" }}>
      <div style={{ position: "relative", maxWidth: "90vw", maxHeight: "90vh" }}>
        <img src={lightbox.photo_url} alt="" style={{ maxWidth: "90vw", maxHeight: "80vh", objectFit: "contain", borderRadius: 8 }} />
        <div style={{ textAlign: "center", marginTop: 12 }}>
          <p style={{ color: "#fff", fontSize: 16, fontWeight: 600 }}>{lightbox.name || "Unknown"}</p>
          <p style={{ color: "#aaa", fontSize: 13 }}>{lightbox.class} · {lightbox.last_seen?.slice(0, 10)}</p>
        </div>
        <button onClick={() => { setLightbox(null); setTimeout(() => window.scrollTo(0, window._scrollY || 0), 50); }} style={{ position: "absolute", top: -40, right: 0, background: "none", border: "none", color: "#fff", fontSize: 24, cursor: "pointer" }}>✕</button>
      </div>
    </div>
  );

  if (plan !== "premium") return (
    <div style={{ maxWidth: 500, textAlign: "center", paddingTop: 60 }}>
      <div style={{ fontSize: 48, marginBottom: 16 }}>🔍</div>
      <h2 style={{ fontSize: 22, fontWeight: 700, color: "#111", marginBottom: 12 }}>Subject Recognition</h2>
      <p style={{ color: "#888", fontSize: 14, lineHeight: 1.6, marginBottom: 24 }}>
        Automatically detect and identify people and objects across all your cameras. Name them and get personalized alerts.
      </p>
      <div style={{ background: "#f9f9f9", border: "1px solid #eee", borderRadius: 12, padding: 24, marginBottom: 24 }}>
        {["Automatic crop of every detected subject", "Name people and objects", "Personalized alerts: 'John arrived'", "Track frequency and history"].map((f, i) => (
          <div key={i} style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 12 }}>
            <span style={{ color: "#00cc66", fontSize: 16 }}>✓</span>
            <span style={{ color: "#555", fontSize: 14 }}>{f}</span>
          </div>
        ))}
      </div>
      <button style={{ background: "#00cc66", color: "#fff", border: "none", padding: "14px 32px", borderRadius: 8, cursor: "pointer", fontWeight: 600, fontSize: 15, width: "100%" }}>
        Upgrade to Premium — $49/mo
      </button>
    </div>
  );

  if (loading) return <div style={{ color: "#888", padding: 40, textAlign: "center" }}>Loading...</div>;

  return (
    <div style={{ maxWidth: 600 }}>
      <h1 style={{ fontFamily: "monospace", fontSize: 28, fontWeight: 700, color: "#111", marginBottom: 8 }}>Subjects</h1>
      <p style={{ color: "#888", fontSize: 14, marginBottom: 24 }}>{subjects.length} detected subjects across all cameras</p>

      {subjects.length === 0 ? (
        <div style={{ textAlign: "center", padding: 60, color: "#aaa" }}>
          <div style={{ fontSize: 40, marginBottom: 12 }}>👤</div>
          <p>No subjects detected yet. Subjects appear when cameras detect people or objects.</p>
        </div>
      ) : (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(160px, 1fr))", gap: 12 }}>
          {subjects.map(s => (
            <div key={s.id} style={card}>
              <div style={{ position: "relative", paddingTop: "100%", background: "#f5f5f7", cursor: "zoom-in" }} onClick={() => { if (s.photo_url) { window._scrollY = window.scrollY; setLightbox(s); } }}>
                {s.photo_url ? (
                  <img src={s.photo_url} alt="" style={{ position: "absolute", top: 0, left: 0, width: "100%", height: "100%", objectFit: "cover" }} />
                ) : (
                  <div style={{ position: "absolute", top: 0, left: 0, width: "100%", height: "100%", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 32 }}>👤</div>
                )}
                <div style={{ position: "absolute", top: 6, right: 6, background: "#111", color: "#fff", borderRadius: 20, padding: "2px 8px", fontSize: 10 }}>{s.class}</div>
                {s.seen_count > 1 && <div style={{ position: "absolute", top: 6, left: 6, background: "#00cc66", color: "#fff", borderRadius: 20, padding: "2px 8px", fontSize: 10 }}>×{s.seen_count}</div>}
                <div style={{ position: "absolute", bottom: 6, right: 6, background: "rgba(0,0,0,0.5)", color: "#fff", borderRadius: 4, padding: "2px 6px", fontSize: 10 }}>🔍</div>
              </div>
              <div style={{ padding: 10 }}>
                {editing === s.id ? (
                  <div>
                    <input style={input} value={editName} onChange={e => setEditName(e.target.value)} placeholder="Enter name" autoFocus onKeyDown={e => e.key === "Enter" && saveName(s.id)} />
                    <div style={{ display: "flex", gap: 6, marginTop: 6 }}>
                      <button onClick={() => saveName(s.id)} style={{ flex: 1, background: "#111", color: "#fff", border: "none", borderRadius: 6, padding: "6px", cursor: "pointer", fontSize: 11 }}>Save</button>
                      <button onClick={() => setEditing(null)} style={{ flex: 1, background: "none", border: "1px solid #ddd", borderRadius: 6, padding: "6px", cursor: "pointer", fontSize: 11 }}>Cancel</button>
                    </div>
                  </div>
                ) : (
                  <div>
                    <div style={{ fontWeight: 600, color: "#111", fontSize: 13, marginBottom: 4 }}>{s.name || "Unknown"}</div>
                    {s.name && !s.name.startsWith("Unknown") && (
                      <div style={{ display: "inline-block", background: "#e6fff4", color: "#009950", borderRadius: 20, padding: "2px 8px", fontSize: 10, fontWeight: 600, marginBottom: 4 }}>⭐ Recognized</div>
                    )}
                    <div style={{ color: "#888", fontSize: 11, marginBottom: 2 }}>📷 Camera {s.camera_id}</div>
                    <div style={{ color: "#aaa", fontSize: 10, marginBottom: 6 }}>Last: {s.last_seen?.slice(0, 16)}</div>
                    <div style={{ display: "flex", gap: 6 }}>
                      <button onClick={() => { setEditing(s.id); setEditName(s.name || ""); }} style={{ flex: 1, background: "none", border: "1px solid #ddd", borderRadius: 6, padding: "5px", cursor: "pointer", fontSize: 11, color: "#555" }}>✏️ Name</button>
                      <button onClick={() => deleteSubject(s.id)} style={{ background: "none", border: "1px solid #ffcccc", borderRadius: 6, padding: "5px 8px", cursor: "pointer", fontSize: 11, color: "#ff3366" }}>✕</button>
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
