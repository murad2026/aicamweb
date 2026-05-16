import { useState } from "react";
import api from "./api";

const BRANDS = [
  { id: "unifi", name: "Ubiquiti UniFi", manual: true },
  { id: "hikvision", name: "Hikvision", rtsp: "rtsp://{user}:{pass}@{ip}/Streaming/Channels/101" },
  { id: "dahua", name: "Dahua", rtsp: "rtsp://{user}:{pass}@{ip}/cam/realmonitor?channel=1&subtype=0" },
  { id: "reolink", name: "Reolink", rtsp: "rtsp://{user}:{pass}@{ip}/h264Preview_01_main" },
  { id: "other", name: "Other (manual RTSP)", manual: true },
];

const CLASSES = ["person", "car", "motorcycle", "bicycle", "cat", "dog", "bus", "truck"];

export default function AddCamera({ onBack }) {
  const [step, setStep] = useState(1);
  const [brand, setBrand] = useState(null);
  const [form, setForm] = useState({ name: "", ip: "", user: "", pass: "", rtsp_url: "", telegram_username: "" });
  const [selected, setSelected] = useState(["person"]);
  const [loading, setLoading] = useState(false);
  const [scanning, setScanning] = useState(false);
  const [foundCameras, setFoundCameras] = useState([]);
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState(null);

  const toggleClass = function(cls) {
    setSelected(function(prev) {
      return prev.includes(cls) ? prev.filter(function(c) { return c !== cls; }) : [...prev, cls];
    });
  };

  const scanNetwork = async function() {
    setScanning(true);
    setFoundCameras([]);
    try {
      const r = await api.get("/scan");
      setFoundCameras(r.data.cameras);
    } catch(e) {
      console.error(e);
    }
    setScanning(false);
  };

  const selectFound = function(cam) {
    setForm({ ...form, ip: cam.ip });
    if (cam.type === "unifi") {
      setBrand(BRANDS.find(function(b) { return b.id === "unifi"; }));
    }
    setStep(2);
  };

  const testConnection = async function() {
    setTesting(true);
    setTestResult(null);
    try {
      const r = await api.post("/test-rtsp", {
        ip: form.ip, username: form.user, password: form.pass, brand: brand?.id || "generic"
      });
      setTestResult(r.data);
      if (r.data.success) {
        setForm({ ...form, rtsp_url: r.data.rtsp_url });
      }
    } catch(e) {
      setTestResult({ success: false });
    }
    setTesting(false);
  };

  const buildRtsp = function() {
    if (!brand) return "";
    if (brand.manual) return form.rtsp_url;
    return brand.rtsp.replace("{ip}", form.ip).replace("{user}", form.user).replace("{pass}", form.pass);
  };

  const save = async function() {
    setLoading(true);
    const rtsp = buildRtsp();
    await api.post("/cameras", {
      name: form.name, rtsp_url: rtsp, brand: brand ? brand.id : "other",
      detect_classes: selected, notify_telegram: form.telegram_username || null,
    });
    setLoading(false);
    onBack();
  };

  const input = {
    background: "#1a1a1a", border: "1px solid #333", borderRadius: 8,
    padding: "12px 16px", color: "#f0f0f0", fontSize: 14, width: "100%",
    fontFamily: "sans-serif", outline: "none", marginBottom: 16, display: "block"
  };
  const label = { fontSize: 12, color: "#666", marginBottom: 6, display: "block", letterSpacing: 1 };
  const btn = { background: "#00ff88", color: "#000", border: "none", padding: "12px 28px", borderRadius: 8, cursor: "pointer", fontWeight: 500, width: "100%", fontSize: 14 };

  return (
    <div style={{ maxWidth: 600 }}>
      <button onClick={onBack} style={{ background: "none", border: "none", color: "#555", cursor: "pointer", marginBottom: 32 }}>← Back</button>
      <h2 style={{ fontSize: 24, marginBottom: 8, color: "#f0f0f0", fontFamily: "monospace" }}>Add Camera</h2>

      <div style={{ display: "flex", gap: 8, marginBottom: 32 }}>
        {["Brand", "Details", "Detect", "Alerts"].map(function(s, i) {
          return (
            <div key={s} style={{
              flex: 1, textAlign: "center", fontSize: 11, padding: "6px", borderRadius: 6, fontWeight: 500,
              background: step === i + 1 ? "#00ff88" : step > i + 1 ? "#001a0d" : "#111",
              color: step === i + 1 ? "#000" : step > i + 1 ? "#00ff88" : "#333"
            }}>{s}</div>
          );
        })}
      </div>

      {step === 1 && (
        <div>
          <button onClick={scanNetwork} disabled={scanning} style={{
            background: "#0a1a0a", border: "1px solid #00ff88", color: "#00ff88",
            padding: "14px", borderRadius: 10, cursor: "pointer", width: "100%",
            marginBottom: 20, fontSize: 14, fontWeight: 500
          }}>
            {scanning ? "🔍 Scanning network..." : "🔍 Scan my network"}
          </button>

          {foundCameras.length > 0 && (
            <div style={{ marginBottom: 20 }}>
              <p style={{ color: "#555", fontSize: 12, marginBottom: 10 }}>Found {foundCameras.length} camera(s):</p>
              {foundCameras.map(function(cam, i) {
                return (
                  <div key={i} onClick={function() { selectFound(cam); }}
                    style={{ border: "1px solid #222", borderRadius: 10, padding: "14px 20px", marginBottom: 8, cursor: "pointer", background: "#111", display: "flex", justifyContent: "space-between", alignItems: "center" }}
                    onMouseEnter={function(e) { e.currentTarget.style.borderColor = "#00ff88"; }}
                    onMouseLeave={function(e) { e.currentTarget.style.borderColor = "#222"; }}
                  >
                    <div>
                      <span style={{ color: "#f0f0f0", fontWeight: 500 }}>{cam.ip}</span>
                      <span style={{ color: "#444", fontSize: 12, marginLeft: 10 }}>:{cam.port}</span>
                    </div>
                    <span style={{ color: "#00ff88", fontSize: 11, background: "#001a0d", padding: "3px 10px", borderRadius: 20 }}>{cam.type}</span>
                  </div>
                );
              })}
            </div>
          )}

          <p style={{ color: "#333", fontSize: 12, marginBottom: 16, textAlign: "center" }}>— or select manually —</p>

          {BRANDS.map(function(b) {
            return (
              <div key={b.id} onClick={function() { setBrand(b); setStep(2); }}
                style={{ border: "1px solid #222", borderRadius: 10, padding: "16px 20px", marginBottom: 10, cursor: "pointer", background: "#111", color: "#f0f0f0", fontWeight: 500 }}
                onMouseEnter={function(e) { e.currentTarget.style.borderColor = "#00ff88"; }}
                onMouseLeave={function(e) { e.currentTarget.style.borderColor = "#222"; }}
              >{b.name}</div>
            );
          })}
        </div>
      )}

      {step === 2 && (
        <div>
          <label style={label}>CAMERA NAME</label>
          <input style={input} placeholder="e.g. Front Door" value={form.name} onChange={function(e) { setForm({ ...form, name: e.target.value }); }} />

          {brand && brand.manual ? (
            <div>
              <label style={label}>RTSP / RTSPS URL</label>
              <input style={input} placeholder={brand.id === "unifi" ? "rtsps://192.168.1.x:7441/..." : "rtsp://..."} value={form.rtsp_url} onChange={function(e) { setForm({ ...form, rtsp_url: e.target.value }); }} />
              {brand.id === "unifi" && <p style={{ color: "#333", fontSize: 12, marginTop: -10, marginBottom: 16 }}>Find in UniFi Protect → Camera → Settings → RTSP</p>}
            </div>
          ) : (
            <div>
              <label style={label}>CAMERA IP</label>
              <input style={input} placeholder="192.168.1.x" value={form.ip} onChange={function(e) { setForm({ ...form, ip: e.target.value }); }} />
              <label style={label}>USERNAME</label>
              <input style={input} placeholder="admin" value={form.user} onChange={function(e) { setForm({ ...form, user: e.target.value }); }} />
              <label style={label}>PASSWORD</label>
              <input style={input} type="password" value={form.pass} onChange={function(e) { setForm({ ...form, pass: e.target.value }); }} />
              <button onClick={testConnection} disabled={testing} style={{
                background: "#111", border: "1px solid #333", color: "#666",
                padding: "10px", borderRadius: 8, cursor: "pointer", width: "100%", marginBottom: 16
              }}>
                {testing ? "Testing..." : testResult?.success ? "✓ Connected!" : "Test Connection"}
              </button>
              {testResult && !testResult.success && <p style={{ color: "#ff3366", fontSize: 12, marginBottom: 16 }}>Could not connect. Check credentials.</p>}
            </div>
          )}
          <button onClick={function() { setStep(3); }} style={btn}>Continue →</button>
        </div>
      )}

      {step === 3 && (
        <div>
          <p style={{ color: "#666", marginBottom: 24 }}>What should trigger alerts?</p>
          <div style={{ display: "flex", flexWrap: "wrap", gap: 10, marginBottom: 32 }}>
            {CLASSES.map(function(cls) {
              return (
                <div key={cls} onClick={function() { toggleClass(cls); }} style={{
                  padding: "10px 20px", borderRadius: 8, cursor: "pointer",
                  border: selected.includes(cls) ? "1px solid #00ff88" : "1px solid #333",
                  background: selected.includes(cls) ? "#001a0d" : "#111",
                  color: selected.includes(cls) ? "#00ff88" : "#666", fontWeight: 500
                }}>{cls}</div>
              );
            })}
          </div>
          <button onClick={function() { setStep(4); }} style={btn}>Continue →</button>
        </div>
      )}

      {step === 4 && (
        <div>
          <p style={{ color: "#666", marginBottom: 24 }}>Where should alerts go?</p>
          <div style={{ background: "#111", border: "1px solid #222", borderRadius: 10, padding: 20, marginBottom: 24 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 12 }}>
              <span style={{ fontSize: 20 }}>✈️</span>
              <span style={{ color: "#f0f0f0", fontWeight: 500 }}>Telegram</span>
            </div>
            <label style={label}>TELEGRAM USERNAME</label>
            <input style={input} placeholder="@username" value={form.telegram_username} onChange={function(e) { setForm({ ...form, telegram_username: e.target.value }); }} />
            <p style={{ color: "#333", fontSize: 11 }}>User must send /start to @aianycamera_bot first</p>
          </div>
          <button onClick={save} disabled={loading} style={btn}>
            {loading ? "Saving..." : "Save Camera ✓"}
          </button>
        </div>
      )}
    </div>
  );
}
