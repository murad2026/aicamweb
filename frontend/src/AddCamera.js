import { useState } from "react";
import api from "./api";

const CLASSES = ["person", "car", "bicycle", "motorcycle", "bus", "truck", "cat", "dog"];

export default function AddCamera({ onBack, user }) {
  const [mode, setMode] = useState(null); // "single" | "dvr"
  const [step, setStep] = useState(1);
  const [form, setForm] = useState({ ip: "", user: "admin", pass: "" });
  const [selected, setSelected] = useState(["person"]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showUpgrade, setShowUpgrade] = useState(false);
  const [upgradeReason, setUpgradeReason] = useState("");
  // DVR specific
  const [channels, setChannels] = useState(8);
  const [selectedChannels, setSelectedChannels] = useState([1,2,3,4,5,6,7,8]);
  const [bulkResults, setBulkResults] = useState(null); // {added, failed, skipped}

  const plan = user?.plan || "free";
  const camCount = user?.cam_count || 0;

  const toggleClass = (cls) => setSelected(prev => prev.includes(cls) ? prev.filter(c => c !== cls) : [...prev, cls]);
  const toggleChannel = (ch) => setSelectedChannels(prev => prev.includes(ch) ? prev.filter(c => c !== ch) : [...prev, ch].sort((a,b)=>a-b));

  const input = { background: "#f5f5f7", border: "1px solid #ddd", borderRadius: 8, padding: "12px 16px", color: "#111", fontSize: 14, width: "100%", fontFamily: "sans-serif", outline: "none", marginBottom: 16, display: "block", boxSizing: "border-box" };
  const label = { fontSize: 11, color: "#888", marginBottom: 6, display: "block", letterSpacing: 1 };
  const btn = { background: "#00cc66", color: "#fff", border: "none", padding: "14px", borderRadius: 8, cursor: "pointer", fontWeight: 600, width: "100%", fontSize: 14 };

  // Connect single camera
  const connectSingle = async () => {
    if (!form.ip) { setError("Enter camera IP address"); return; }
    if (!form.pass) { setError("Enter password"); return; }
    setLoading(true);
    setError(null);
    try {
      await api.post("/cameras/auto-add", {
        ip: form.ip,
        username: form.user,
        password: form.pass,
        detect_classes: selected,
        name: form.name || null,
      });
      onBack();
    } catch(err) {
      const detail = err.response?.data?.detail || err.message;
      if (detail?.startsWith("UPGRADE_REQUIRED:")) {
        setUpgradeReason(detail.replace("UPGRADE_REQUIRED: ", ""));
        setShowUpgrade(true);
      } else if (err.response?.status === 409) {
        setError("This camera is already added.");
      } else if (err.response?.status === 400) {
        setError("Cannot connect. Check the IP address, username and password.");
      } else {
        setError("Error: " + detail);
      }
    }
    setLoading(false);
  };

  // Connect DVR bulk
  const connectDVR = async () => {
    if (!form.ip) { setError("Enter DVR IP address"); return; }
    if (!form.pass) { setError("Enter password"); return; }
    if (selectedChannels.length === 0) { setError("Select at least one channel"); return; }
    setLoading(true);
    setError(null);
    const results = { added: [], failed: [], skipped: [] };
    for (const ch of selectedChannels) {
      const rtsp = `rtsp://${form.user}:${form.pass}@${form.ip}:554/cam/realmonitor?channel=${ch}&subtype=0`;
      const name = `DVR ${form.ip} CH${ch}`;
      try {
        await api.post("/cameras", {
          name,
          rtsp_url: rtsp,
          brand: "dahua",
          detect_classes: selected,
        });
        results.added.push(ch);
      } catch(err) {
        if (err.response?.status === 409) {
          results.skipped.push(ch);
        } else if (err.response?.data?.detail?.startsWith("UPGRADE_REQUIRED:")) {
          setUpgradeReason(err.response.data.detail.replace("UPGRADE_REQUIRED: ", ""));
          setShowUpgrade(true);
          setLoading(false);
          return;
        } else {
          results.failed.push(ch);
        }
      }
    }
    setLoading(false);
    setBulkResults(results);
  };

  // Upgrade modal
  if (showUpgrade) return (
    <div style={{ position: "fixed", top: 0, left: 0, right: 0, bottom: 0, background: "rgba(0,0,0,0.5)", display: "flex", alignItems: "center", justifyContent: "center", zIndex: 1000 }}>
      <div style={{ background: "#fff", borderRadius: 16, padding: 32, maxWidth: 380, width: "90%", textAlign: "center" }}>
        <div style={{ fontSize: 40, marginBottom: 16 }}>⚡️</div>
        <h3 style={{ fontSize: 20, fontWeight: 700, marginBottom: 12, color: "#111" }}>Upgrade Required</h3>
        <p style={{ color: "#888", fontSize: 14, marginBottom: 24, lineHeight: 1.6 }}>{upgradeReason}</p>
        <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
          <button onClick={async () => { await api.post("/auth/upgrade", { plan: "pro" }); window.location.reload(); }} style={{ background: "#111", color: "#fff", border: "none", padding: "14px", borderRadius: 8, cursor: "pointer", fontWeight: 600, fontSize: 14 }}>Upgrade to Pro — $19/mo</button>
          <button onClick={async () => { await api.post("/auth/upgrade", { plan: "premium" }); window.location.reload(); }} style={{ background: "#00cc66", color: "#fff", border: "none", padding: "14px", borderRadius: 8, cursor: "pointer", fontWeight: 600, fontSize: 14 }}>Upgrade to Premium — $49/mo</button>
          <button onClick={() => setShowUpgrade(false)} style={{ background: "none", border: "1px solid #ddd", color: "#888", padding: "12px", borderRadius: 8, cursor: "pointer", fontSize: 13 }}>Maybe later</button>
        </div>
      </div>
    </div>
  );

  // Bulk results screen
  if (bulkResults) return (
    <div style={{ maxWidth: 480 }}>
      <h2 style={{ fontFamily: "monospace", fontSize: 24, marginBottom: 24, color: "#111" }}>DVR Import Complete</h2>
      {bulkResults.added.length > 0 && (
        <div style={{ background: "#e6fff4", border: "1px solid #00cc66", borderRadius: 10, padding: 16, marginBottom: 12 }}>
          <p style={{ color: "#009950", fontWeight: 600, margin: "0 0 6px" }}>✅ Added {bulkResults.added.length} cameras</p>
          <p style={{ color: "#555", fontSize: 13, margin: 0 }}>Channels: {bulkResults.added.join(", ")}</p>
        </div>
      )}
      {bulkResults.skipped.length > 0 && (
        <div style={{ background: "#fff8e6", border: "1px solid #ffcc66", borderRadius: 10, padding: 16, marginBottom: 12 }}>
          <p style={{ color: "#cc8800", fontWeight: 600, margin: "0 0 6px" }}>⚠️ Already added: {bulkResults.skipped.length}</p>
          <p style={{ color: "#555", fontSize: 13, margin: 0 }}>Channels: {bulkResults.skipped.join(", ")}</p>
        </div>
      )}
      {bulkResults.failed.length > 0 && (
        <div style={{ background: "#fff0f0", border: "1px solid #ffcccc", borderRadius: 10, padding: 16, marginBottom: 12 }}>
          <p style={{ color: "#cc0000", fontWeight: 600, margin: "0 0 6px" }}>❌ Failed: {bulkResults.failed.length}</p>
          <p style={{ color: "#555", fontSize: 13, margin: 0 }}>Channels: {bulkResults.failed.join(", ")}</p>
        </div>
      )}
      <button onClick={onBack} style={{ ...btn, marginTop: 16 }}>Go to Dashboard</button>
    </div>
  );

  // Mode selection
  if (!mode) return (
    <div style={{ maxWidth: 480 }}>
      <button onClick={onBack} style={{ background: "none", border: "none", color: "#555", cursor: "pointer", marginBottom: 32, fontSize: 14 }}>← Back</button>
      <h2 style={{ fontFamily: "monospace", fontSize: 24, marginBottom: 8, color: "#111" }}>Add Camera</h2>
      <p style={{ color: "#888", fontSize: 14, marginBottom: 32, lineHeight: 1.6 }}>What type of camera are you adding?</p>
      <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
        <div onClick={() => setMode("single")} style={{ border: "1px solid #ddd", borderRadius: 12, padding: 20, cursor: "pointer", background: "#fff", display: "flex", alignItems: "center", gap: 16 }}>
          <span style={{ fontSize: 32 }}>📷</span>
          <div>
            <p style={{ fontWeight: 600, color: "#111", margin: "0 0 4px" }}>Single IP Camera</p>
            <p style={{ color: "#888", fontSize: 13, margin: 0 }}>Hikvision, Dahua, Axis, or any RTSP camera</p>
          </div>
        </div>
        <div onClick={() => setMode("dvr")} style={{ border: "1px solid #ddd", borderRadius: 12, padding: 20, cursor: "pointer", background: "#fff", display: "flex", alignItems: "center", gap: 16 }}>
          <span style={{ fontSize: 32 }}>🎛️</span>
          <div>
            <p style={{ fontWeight: 600, color: "#111", margin: "0 0 4px" }}>DVR / NVR — Bulk Add</p>
            <p style={{ color: "#888", fontSize: 13, margin: 0 }}>Add multiple channels from a recorder at once</p>
          </div>
        </div>
        <div onClick={() => setMode("rtsp")} style={{ border: "1px solid #ddd", borderRadius: 12, padding: 20, cursor: "pointer", background: "#fff", display: "flex", alignItems: "center", gap: 16 }}>
          <span style={{ fontSize: 32 }}>🔗</span>
          <div>
            <p style={{ fontWeight: 600, color: "#111", margin: "0 0 4px" }}>RTSP(S) URL — Direct</p>
            <p style={{ color: "#888", fontSize: 13, margin: 0 }}>Paste RTSP(S) link directly</p>
          </div>
        </div>
      </div>
    </div>
  );

  // Single camera flow
  if (mode === "single") return (
    <div style={{ maxWidth: 480 }}>
      <button onClick={step === 1 ? () => setMode(null) : () => setStep(1)} style={{ background: "none", border: "none", color: "#555", cursor: "pointer", marginBottom: 32, fontSize: 14 }}>← Back</button>
      {step === 1 && (
        <div>
          <h2 style={{ fontSize: 24, marginBottom: 8, color: "#111", fontFamily: "monospace" }}>Single Camera</h2>
          <p style={{ color: "#888", fontSize: 14, marginBottom: 28, lineHeight: 1.6 }}>Enter your camera's IP address and login credentials.</p>
          <label style={label}>CAMERA NAME (OPTIONAL)</label>
          <input style={input} placeholder="e.g. Front Door" value={form.name || ""} onChange={e => setForm({ ...form, name: e.target.value })} />
          <label style={label}>CAMERA IP ADDRESS</label>
          <input style={input} placeholder="192.168.1.100" value={form.ip} onChange={e => setForm({ ...form, ip: e.target.value })} />
          <label style={label}>USERNAME</label>
          <input style={input} placeholder="admin" value={form.user} onChange={e => setForm({ ...form, user: e.target.value })} />
          <label style={label}>PASSWORD</label>
          <input style={input} type="password" placeholder="••••••••" value={form.pass} onChange={e => setForm({ ...form, pass: e.target.value })} />
          {error && <p style={{ color: "#ff3366", fontSize: 13, marginBottom: 16 }}>{error}</p>}
          <button onClick={() => setStep(2)} disabled={!form.ip || !form.pass} style={{ ...btn, opacity: (!form.ip || !form.pass) ? 0.5 : 1 }}>Continue →</button>
        </div>
      )}
      {step === 2 && (
        <div>
          <h2 style={{ fontSize: 24, marginBottom: 8, color: "#111", fontFamily: "monospace" }}>What to detect?</h2>
          <p style={{ color: "#888", fontSize: 14, marginBottom: 24 }}>Choose what triggers an alert.</p>
          <div style={{ display: "flex", flexWrap: "wrap", gap: 10, marginBottom: 32 }}>
            {CLASSES.map(cls => (
              <div key={cls} onClick={() => toggleClass(cls)} style={{
                padding: "10px 20px", borderRadius: 8, cursor: "pointer",
                border: selected.includes(cls) ? "1px solid #00cc66" : "1px solid #ddd",
                background: selected.includes(cls) ? "#e6fff4" : "#fff",
                color: selected.includes(cls) ? "#009950" : "#888", fontWeight: 500
              }}>{cls}</div>
            ))}
          </div>
          {error && <p style={{ color: "#ff3366", fontSize: 13, marginBottom: 16 }}>{error}</p>}
          <button onClick={connectSingle} disabled={loading} style={btn}>
            {loading ? "Connecting..." : "Connect Camera"}
          </button>
          {loading && <p style={{ color: "#888", fontSize: 12, textAlign: "center", marginTop: 12 }}>Testing connection, this may take up to 30 seconds...</p>}
        </div>
      )}
    </div>
  );


  // RTSP direct flow
  if (mode === "rtsp") return (
    <div style={{ maxWidth: 480 }}>
      <button onClick={() => setMode(null)} style={{ background: "none", border: "none", color: "#555", cursor: "pointer", marginBottom: 32, fontSize: 14 }}>← Back</button>
      <h2 style={{ fontSize: 24, marginBottom: 8, color: "#111", fontFamily: "monospace" }}>RTSP(S) URL</h2>
      <p style={{ color: "#888", fontSize: 14, marginBottom: 24 }}>Paste your camera RTSP(S) URL directly</p>
      <label style={label}>CAMERA NAME</label>
      <input value={form.name || ""} onChange={e => setForm(f => ({...f, name: e.target.value}))} placeholder="e.g. Front Door" style={input} />
      <label style={label}>RTSP URL</label>
      <input value={form.rtspUrl || ""} onChange={e => setForm(f => ({...f, rtspUrl: e.target.value}))} placeholder="rtsp://user:pass@192.168.1.100:554/stream" style={input} />
      {error && <p style={{ color: "#ff4466", fontSize: 13, marginBottom: 12 }}>{error}</p>}
      <button onClick={async () => {
        setLoading(true); setError(null);
        try {
          await api.post("/cameras", { name: form.name || "Camera", rtsp_url: form.rtspUrl, brand: "generic", detect_classes: ["person"] });
          onBack();
        } catch(e) { setError(e.response?.data?.detail || "Cannot connect to camera"); }
        setLoading(false);
      }} disabled={loading} style={btn}>{loading ? "Connecting..." : "Add Camera"}</button>
    </div>
  );

  // DVR/NVR bulk flow
  if (mode === "dvr") return (
    <div style={{ maxWidth: 480 }}>
      <button onClick={step === 1 ? () => setMode(null) : () => setStep(step - 1)} style={{ background: "none", border: "none", color: "#555", cursor: "pointer", marginBottom: 32, fontSize: 14 }}>← Back</button>

      {step === 1 && (
        <div>
          <h2 style={{ fontSize: 24, marginBottom: 8, color: "#111", fontFamily: "monospace" }}>DVR / NVR</h2>
          <p style={{ color: "#888", fontSize: 14, marginBottom: 28, lineHeight: 1.6 }}>Connect to your recorder and add multiple cameras at once.</p>
          <label style={label}>DVR / NVR IP ADDRESS</label>
          <input style={input} placeholder="192.168.1.100" value={form.ip} onChange={e => setForm({ ...form, ip: e.target.value })} />
          <label style={label}>USERNAME</label>
          <input style={input} placeholder="admin" value={form.user} onChange={e => setForm({ ...form, user: e.target.value })} />
          <label style={label}>PASSWORD</label>
          <input style={input} type="password" placeholder="••••••••" value={form.pass} onChange={e => setForm({ ...form, pass: e.target.value })} />
          <label style={label}>NUMBER OF CHANNELS</label>
          <div style={{ display: "flex", gap: 8, marginBottom: 16 }}>
            {[4, 8, 16, 32].map(n => (
              <div key={n} onClick={() => { setChannels(n); setSelectedChannels(Array.from({length: n}, (_, i) => i + 1)); }} style={{
                flex: 1, textAlign: "center", padding: "10px", borderRadius: 8, cursor: "pointer",
                border: channels === n ? "1px solid #00cc66" : "1px solid #ddd",
                background: channels === n ? "#e6fff4" : "#fff",
                color: channels === n ? "#009950" : "#888", fontWeight: 600
              }}>{n}</div>
            ))}
          </div>
          {error && <p style={{ color: "#ff3366", fontSize: 13, marginBottom: 16 }}>{error}</p>}
          <button onClick={() => setStep(2)} disabled={!form.ip || !form.pass} style={{ ...btn, opacity: (!form.ip || !form.pass) ? 0.5 : 1 }}>Continue →</button>
        </div>
      )}

      {step === 2 && (
        <div>
          <h2 style={{ fontSize: 24, marginBottom: 8, color: "#111", fontFamily: "monospace" }}>Select Channels</h2>
          <p style={{ color: "#888", fontSize: 14, marginBottom: 20 }}>Choose which channels to add. Tap to toggle.</p>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 8, marginBottom: 20 }}>
            {Array.from({length: channels}, (_, i) => i + 1).map(ch => (
              <div key={ch} onClick={() => toggleChannel(ch)} style={{
                textAlign: "center", padding: "12px 8px", borderRadius: 8, cursor: "pointer",
                border: selectedChannels.includes(ch) ? "1px solid #00cc66" : "1px solid #ddd",
                background: selectedChannels.includes(ch) ? "#e6fff4" : "#fff",
                color: selectedChannels.includes(ch) ? "#009950" : "#888", fontWeight: 600, fontSize: 14
              }}>CH {ch}</div>
            ))}
          </div>
          <div style={{ display: "flex", gap: 8, marginBottom: 24 }}>
            <button onClick={() => setSelectedChannels(Array.from({length: channels}, (_, i) => i + 1))} style={{ flex: 1, background: "none", border: "1px solid #ddd", borderRadius: 8, padding: "8px", cursor: "pointer", fontSize: 12, color: "#555" }}>Select All</button>
            <button onClick={() => setSelectedChannels([])} style={{ flex: 1, background: "none", border: "1px solid #ddd", borderRadius: 8, padding: "8px", cursor: "pointer", fontSize: 12, color: "#555" }}>Clear</button>
          </div>
          <button onClick={() => setStep(3)} disabled={selectedChannels.length === 0} style={{ ...btn, opacity: selectedChannels.length === 0 ? 0.5 : 1 }}>Continue →</button>
        </div>
      )}

      {step === 3 && (
        <div>
          <h2 style={{ fontSize: 24, marginBottom: 8, color: "#111", fontFamily: "monospace" }}>What to detect?</h2>
          <p style={{ color: "#888", fontSize: 14, marginBottom: 24 }}>Choose what triggers alerts on all {selectedChannels.length} channels.</p>
          <div style={{ display: "flex", flexWrap: "wrap", gap: 10, marginBottom: 24 }}>
            {CLASSES.map(cls => (
              <div key={cls} onClick={() => toggleClass(cls)} style={{
                padding: "10px 20px", borderRadius: 8, cursor: "pointer",
                border: selected.includes(cls) ? "1px solid #00cc66" : "1px solid #ddd",
                background: selected.includes(cls) ? "#e6fff4" : "#fff",
                color: selected.includes(cls) ? "#009950" : "#888", fontWeight: 500
              }}>{cls}</div>
            ))}
          </div>
          <div style={{ background: "#f5f5f7", borderRadius: 10, padding: 14, marginBottom: 20 }}>
            <p style={{ color: "#555", fontSize: 13, margin: 0 }}>
              Adding <strong>{selectedChannels.length} channels</strong> from DVR <strong>{form.ip}</strong><br />
              Channels: {selectedChannels.join(", ")}
            </p>
          </div>
          {error && <p style={{ color: "#ff3366", fontSize: 13, marginBottom: 16 }}>{error}</p>}
          <button onClick={connectDVR} disabled={loading} style={btn}>
            {loading ? `Adding channels... (${selectedChannels.length} total)` : `Add ${selectedChannels.length} Cameras`}
          </button>
          {loading && <p style={{ color: "#888", fontSize: 12, textAlign: "center", marginTop: 12 }}>This may take a minute...</p>}
        </div>
      )}
    </div>
  );
}
