import { useState } from "react";
import api from "./api";

export default function Account({ user, onLogout }) {
  const [changing, setChanging] = useState(false);
  const [form, setForm] = useState({ current_password: "", new_password: "", confirm: "" });
  const [msg, setMsg] = useState(null);
  const [loading, setLoading] = useState(false);

  const input = {
    background: "#1a1a1a", border: "1px solid #333", borderRadius: 8,
    padding: "12px 16px", color: "#f0f0f0", fontSize: 14, width: "100%",
    fontFamily: "sans-serif", outline: "none", marginBottom: 16, display: "block"
  };
  const label = { fontSize: 12, color: "#666", marginBottom: 6, display: "block", letterSpacing: 1 };

  const changePassword = async function() {
    if (form.new_password !== form.confirm) {
      setMsg({ type: "error", text: "Passwords don't match" });
      return;
    }
    setLoading(true);
    try {
      await api.post("/auth/change-password", {
        current_password: form.current_password,
        new_password: form.new_password
      });
      setMsg({ type: "success", text: "Password changed!" });
      setChanging(false);
      setForm({ current_password: "", new_password: "", confirm: "" });
    } catch(e) {
      setMsg({ type: "error", text: e.response?.data?.detail || "Error" });
    }
    setLoading(false);
  };

  return (
    <div style={{ maxWidth: 500 }}>
      <h1 style={{ fontFamily: "monospace", fontSize: 28, fontWeight: 700, color: "#f0f0f0", marginBottom: 32 }}>Account</h1>

      <div style={{ background: "#111", border: "1px solid #222", borderRadius: 12, padding: 24, marginBottom: 16 }}>
        <div style={{ marginBottom: 16 }}>
          <label style={label}>USERNAME</label>
          <p style={{ color: "#f0f0f0", fontSize: 16 }}>{user.username}</p>
        </div>
        <div style={{ marginBottom: 16 }}>
          <label style={label}>EMAIL</label>
          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <p style={{ color: "#f0f0f0", fontSize: 16 }}>{user.email}</p>
            {user.is_verified
              ? <span style={{ background: "#001a0d", color: "#00ff88", padding: "2px 10px", borderRadius: 20, fontSize: 11 }}>✓ Verified</span>
              : <span style={{ background: "#1a0a00", color: "#ff6600", padding: "2px 10px", borderRadius: 20, fontSize: 11 }}>⚠ Not verified</span>
            }
          </div>
        </div>
      </div>

      <div style={{ background: "#111", border: "1px solid #222", borderRadius: 12, padding: 24, marginBottom: 16 }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: changing ? 16 : 0 }}>
          <span style={{ color: "#f0f0f0", fontWeight: 500 }}>Password</span>
          <button onClick={function() { setChanging(!changing); setMsg(null); }} style={{
            background: "none", border: "1px solid #333", color: "#666",
            padding: "6px 14px", borderRadius: 6, cursor: "pointer", fontSize: 12
          }}>{changing ? "Cancel" : "Change"}</button>
        </div>

        {changing && (
          <div>
            <label style={label}>CURRENT PASSWORD</label>
            <input style={input} type="password" value={form.current_password} onChange={function(e) { setForm({ ...form, current_password: e.target.value }); }} />
            <label style={label}>NEW PASSWORD</label>
            <input style={input} type="password" value={form.new_password} onChange={function(e) { setForm({ ...form, new_password: e.target.value }); }} />
            <label style={label}>CONFIRM PASSWORD</label>
            <input style={input} type="password" value={form.confirm} onChange={function(e) { setForm({ ...form, confirm: e.target.value }); }} />
            {msg && <p style={{ color: msg.type === "error" ? "#ff3366" : "#00ff88", fontSize: 13, marginBottom: 16 }}>{msg.text}</p>}
            <button onClick={changePassword} disabled={loading} style={{
              background: "#00ff88", color: "#000", border: "none", padding: "12px", borderRadius: 8, cursor: "pointer", fontWeight: 500, width: "100%"
            }}>{loading ? "Saving..." : "Save New Password"}</button>
          </div>
        )}
      </div>

      <button onClick={onLogout} style={{
        background: "none", border: "1px solid #2a0a0a", color: "#ff3366",
        padding: "12px", borderRadius: 8, cursor: "pointer", width: "100%", fontSize: 14
      }}>Logout</button>
    </div>
  );
}
