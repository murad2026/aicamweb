import { useState } from "react";
import api from "./api";

export default function ResetPassword({ token, onDone }) {
  const [form, setForm] = useState({ password: "", confirm: "" });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  const input = {
    background: "#1a1a1a", border: "1px solid #333", borderRadius: 8,
    padding: "12px 16px", color: "#f0f0f0", fontSize: 14, width: "100%",
    fontFamily: "sans-serif", outline: "none", marginBottom: 16, display: "block"
  };
  const label = { fontSize: 12, color: "#666", marginBottom: 6, display: "block", letterSpacing: 1 };
  const btn = { background: "#00ff88", color: "#000", border: "none", padding: "12px 28px", borderRadius: 8, cursor: "pointer", fontWeight: 700, width: "100%", fontSize: 14 };

  const submit = async function() {
    if (!form.password) { setError("Enter new password"); return; }
    if (form.password !== form.confirm) { setError("Passwords don't match"); return; }
    setLoading(true);
    setError(null);
    try {
      await api.post("/auth/reset-password", { token: token, password: form.password });
      setSuccess(true);
      setTimeout(onDone, 2000);
    } catch(e) {
      setError(e.response?.data?.detail || "Invalid or expired link");
    }
    setLoading(false);
  };

  return (
    <div style={{ minHeight: "100vh", background: "#0a0a0a", display: "flex", alignItems: "center", justifyContent: "center" }}>
      <div style={{ width: 400, padding: 40, background: "#111", borderRadius: 16, border: "1px solid #222" }}>
        <div style={{ textAlign: "center", marginBottom: 32 }}>
          <span style={{ color: "#00ff88", fontSize: 32 }}>⬡</span>
          <h1 style={{ color: "#f0f0f0", fontFamily: "monospace", fontSize: 20, marginTop: 8 }}>AI ANY CAMERA</h1>
          <p style={{ color: "#666", fontSize: 14, marginTop: 8 }}>Reset your password</p>
        </div>

        {success ? (
          <p style={{ textAlign: "center", color: "#00ff88", fontSize: 16 }}>✓ Password changed! Redirecting...</p>
        ) : (
          <div>
            <label style={label}>NEW PASSWORD</label>
            <input style={input} type="password" placeholder="••••••••" value={form.password} onChange={function(e) { setForm({ ...form, password: e.target.value }); }} />
            <label style={label}>CONFIRM PASSWORD</label>
            <input style={input} type="password" placeholder="••••••••" value={form.confirm} onChange={function(e) { setForm({ ...form, confirm: e.target.value }); }} />
            {error && <p style={{ color: "#ff3366", fontSize: 13, marginBottom: 16 }}>{error}</p>}
            <button onClick={submit} disabled={loading} style={btn}>
              {loading ? "Saving..." : "Set New Password"}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
