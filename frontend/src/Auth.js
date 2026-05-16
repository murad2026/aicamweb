import { useState } from "react";
import api from "./api";

export default function Auth({ onLogin }) {
  const [mode, setMode] = useState("login");
  const [form, setForm] = useState({ email: "", username: "", password: "" });
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const input = {
    background: "#1a1a1a", border: "1px solid #333", borderRadius: 8,
    padding: "12px 16px", color: "#f0f0f0", fontSize: 14, width: "100%",
    fontFamily: "sans-serif", outline: "none", marginBottom: 16, display: "block"
  };
  const label = { fontSize: 12, color: "#666", marginBottom: 6, display: "block", letterSpacing: 1 };
  const btn = { background: "#00ff88", color: "#000", border: "none", padding: "12px 28px", borderRadius: 8, cursor: "pointer", fontWeight: 500, width: "100%", fontSize: 14 };

  const submit = async function() {
    setLoading(true);
    setError(null);
    try {
      const endpoint = mode === "login" ? "/auth/login" : "/auth/register";
      const r = await api.post(endpoint, form);
      localStorage.setItem("token", r.data.token);
      localStorage.setItem("user", JSON.stringify(r.data.user));
      onLogin(r.data.user);
    } catch(e) {
      setError(e.response?.data?.detail || "Error");
    }
    setLoading(false);
  };

  return (
    <div style={{ minHeight: "100vh", background: "#0a0a0a", display: "flex", alignItems: "center", justifyContent: "center" }}>
      <div style={{ width: 400, padding: 40, background: "#111", borderRadius: 16, border: "1px solid #222" }}>
        <div style={{ textAlign: "center", marginBottom: 32 }}>
          <span style={{ color: "#00ff88", fontSize: 32 }}>⬡</span>
          <h1 style={{ color: "#f0f0f0", fontFamily: "monospace", fontSize: 20, marginTop: 8 }}>AI ANY CAMERA</h1>
        </div>

        <div style={{ display: "flex", gap: 8, marginBottom: 24 }}>
          <button onClick={function() { setMode("login"); }} style={{
            flex: 1, padding: "10px", borderRadius: 8, cursor: "pointer", fontWeight: 500,
            background: mode === "login" ? "#00ff88" : "#1a1a1a",
            color: mode === "login" ? "#000" : "#666",
            border: "1px solid #333"
          }}>Login</button>
          <button onClick={function() { setMode("register"); }} style={{
            flex: 1, padding: "10px", borderRadius: 8, cursor: "pointer", fontWeight: 500,
            background: mode === "register" ? "#00ff88" : "#1a1a1a",
            color: mode === "register" ? "#000" : "#666",
            border: "1px solid #333"
          }}>Register</button>
        </div>

        <label style={label}>EMAIL</label>
        <input style={input} placeholder="you@example.com" value={form.email} onChange={function(e) { setForm({ ...form, email: e.target.value }); }} />

        {mode === "register" && <>
          <label style={label}>USERNAME</label>
          <input style={input} placeholder="username" value={form.username} onChange={function(e) { setForm({ ...form, username: e.target.value }); }} />
        </>}

        <label style={label}>PASSWORD</label>
        <input style={input} type="password" placeholder="••••••••" value={form.password} onChange={function(e) { setForm({ ...form, password: e.target.value }); }} />

        {error && <p style={{ color: "#ff3366", fontSize: 13, marginBottom: 16 }}>{error}</p>}

        <button onClick={submit} disabled={loading} style={btn}>
          {loading ? "..." : mode === "login" ? "Login" : "Create Account"}
        </button>
      </div>
    </div>
  );
}
