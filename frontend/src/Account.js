import { useState } from "react";
import api from "./api";

export default function Account({ user, onLogout }) {
  const [changing, setChanging] = useState(false);
  const [editEmail, setEditEmail] = useState(false);
  const [editTelegram, setEditTelegram] = useState(false);
  const [editPhone, setEditPhone] = useState(false);
  const [phoneStep, setPhoneStep] = useState("idle"); // idle | sent | verified
  const [verifyCode, setVerifyCode] = useState("");
  const [confirmDelete, setConfirmDelete] = useState(false);
  const [form, setForm] = useState({ current_password: "", new_password: "", confirm: "" });
  const [emailForm, setEmailForm] = useState({ email: user.email || "" });
  const [telegramForm, setTelegramForm] = useState({ telegram: user.telegram_username || "" });
  const [phoneForm, setPhoneForm] = useState({ phone: user.phone || "" });
  const [msg, setMsg] = useState(null);
  const [loading, setLoading] = useState(false);

  const input = {
    background: "#f5f5f7", border: "1px solid #ddd", borderRadius: 8,
    padding: "12px 16px", color: "#111", fontSize: 14, width: "100%",
    fontFamily: "sans-serif", outline: "none", marginBottom: 12, display: "block", boxSizing: "border-box"
  };
  const label = { fontSize: 11, color: "#888", marginBottom: 6, display: "block", letterSpacing: 1 };
  const card = { background: "#fff", border: "1px solid #e0e0e0", borderRadius: 12, padding: 24, marginBottom: 12 };
  const btnSecondary = { background: "none", border: "1px solid #ddd", color: "#555", padding: "6px 14px", borderRadius: 6, cursor: "pointer", fontSize: 12 };
  const btnPrimary = { background: "#111", color: "#fff", border: "none", padding: "12px", borderRadius: 8, cursor: "pointer", fontWeight: 500, width: "100%", fontSize: 14 };

  const showMsg = (type, text) => { setMsg({ type, text }); setTimeout(() => setMsg(null), 3000); };

  const changePassword = async function() {
    if (form.new_password !== form.confirm) { showMsg("error", "Passwords don't match"); return; }
    setLoading(true);
    try {
      await api.post("/auth/change-password", { current_password: form.current_password, new_password: form.new_password });
      showMsg("success", "Password changed!");
      setChanging(false);
      setForm({ current_password: "", new_password: "", confirm: "" });
    } catch(e) { showMsg("error", e.response?.data?.detail || "Error"); }
    setLoading(false);
  };

  const updateEmail = async function() {
    setLoading(true);
    try {
      await api.post("/auth/update-profile", { email: emailForm.email });
      showMsg("success", "Email updated!");
      setEditEmail(false);
      user.email = emailForm.email;
    } catch(e) { showMsg("error", e.response?.data?.detail || "Error"); }
    setLoading(false);
  };

  const updateTelegram = async function() {
    setLoading(true);
    try {
      await api.post("/auth/update-profile", { telegram_username: telegramForm.telegram });
      showMsg("success", "Telegram updated!");
      setEditTelegram(false);
    } catch(e) { showMsg("error", e.response?.data?.detail || "Error"); }
    setLoading(false);
  };

  const sendPhoneCode = async function() {
    if (!phoneForm.phone) { showMsg("error", "Enter phone number"); return; }
    setLoading(true);
    try {
      await api.post("/auth/send-phone-verify", { phone: phoneForm.phone });
      setPhoneStep("sent");
      showMsg("success", "Code sent! Check your SMS");
    } catch(e) { showMsg("error", e.response?.data?.detail || "Error"); }
    setLoading(false);
  };

  const verifyPhone = async function() {
    if (!verifyCode) { showMsg("error", "Enter the code"); return; }
    setLoading(true);
    try {
      const res = await api.post("/auth/verify-phone", { code: verifyCode });
      user.phone = res.data.phone;
      user.phone_verified = true;
      setPhoneStep("verified");
      setEditPhone(false);
      setVerifyCode("");
      showMsg("success", "Phone verified!");
    } catch(e) { showMsg("error", e.response?.data?.detail || "Invalid code"); }
    setLoading(false);
  };

  const deleteAccount = async function() {
    setLoading(true);
    try {
      await api.delete("/auth/delete-account");
      onLogout();
    } catch(e) { showMsg("error", "Error deleting account"); }
    setLoading(false);
  };

  return (
    <div style={{ maxWidth: 500 }}>
      <h1 style={{ fontFamily: "monospace", fontSize: 28, fontWeight: 700, color: "#111", marginBottom: 32 }}>Account</h1>

      {msg && (
        <div style={{ background: msg.type === "error" ? "#fff0f0" : "#f0fff8", border: `1px solid ${msg.type === "error" ? "#ffcccc" : "#00cc66"}`, borderRadius: 8, padding: "12px 16px", marginBottom: 16 }}>
          <p style={{ color: msg.type === "error" ? "#cc0000" : "#00aa55", fontSize: 13, margin: 0 }}>{msg.text}</p>
        </div>
      )}

      {/* Profile */}
      <div style={card}>
        <h3 style={{ fontSize: 13, color: "#888", marginBottom: 16, fontWeight: 600, letterSpacing: 1 }}>PROFILE</h3>
        <div style={{ marginBottom: 16 }}>
          <label style={label}>USERNAME</label>
          <p style={{ color: "#111", fontSize: 15, margin: 0 }}>{user.username}</p>
        </div>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
          <div style={{ flex: 1 }}>
            <label style={label}>EMAIL</label>
            {editEmail ? (
              <div>
                <input style={input} type="email" value={emailForm.email} onChange={e => setEmailForm({ email: e.target.value })} />
                <div style={{ display: "flex", gap: 8 }}>
                  <button onClick={updateEmail} disabled={loading} style={{ ...btnSecondary, background: "#111", color: "#fff", border: "none" }}>Save</button>
                  <button onClick={() => setEditEmail(false)} style={btnSecondary}>Cancel</button>
                </div>
              </div>
            ) : (
              <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                <p style={{ color: "#111", fontSize: 15, margin: 0 }}>{user.email}</p>
                {user.is_verified
                  ? <span style={{ background: "#e6fff4", color: "#009950", padding: "2px 8px", borderRadius: 20, fontSize: 11 }}>✓ Verified</span>
                  : <span style={{ background: "#fff3e0", color: "#e65100", padding: "2px 8px", borderRadius: 20, fontSize: 11 }}>⚠ Not verified</span>
                }
              </div>
            )}
          </div>
          {!editEmail && <button onClick={() => setEditEmail(true)} style={{ ...btnSecondary, marginLeft: 12, marginTop: 18 }}>Edit</button>}
        </div>
      </div>

      {/* Telegram */}
      <div style={card}>
        <h3 style={{ fontSize: 13, color: "#888", marginBottom: 16, fontWeight: 600, letterSpacing: 1 }}>TELEGRAM</h3>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
          <div style={{ flex: 1 }}>
            <label style={label}>USERNAME</label>
            {editTelegram ? (
              <div>
                <input style={input} placeholder="@username" value={telegramForm.telegram} onChange={e => setTelegramForm({ telegram: e.target.value })} />
                <div style={{ display: "flex", gap: 8 }}>
                  <button onClick={updateTelegram} disabled={loading} style={{ ...btnSecondary, background: "#111", color: "#fff", border: "none" }}>Save</button>
                  <button onClick={() => setEditTelegram(false)} style={btnSecondary}>Cancel</button>
                </div>
              </div>
            ) : (
              <p style={{ color: "#111", fontSize: 15, margin: 0 }}>{telegramForm.telegram || "Not set"}</p>
            )}
          </div>
          {!editTelegram && <button onClick={() => setEditTelegram(true)} style={{ ...btnSecondary, marginLeft: 12, marginTop: 18 }}>Edit</button>}
        </div>
        <p style={{ color: "#aaa", fontSize: 11, marginTop: 10, marginBottom: 0 }}>Send /start to <a href="https://t.me/aianycamera_bot" target="_blank" rel="noreferrer" style={{ color: "#111" }}>@aianycamera_bot</a> first</p>
      </div>

      {/* Phone / SMS */}
      <div style={card}>
        <h3 style={{ fontSize: 13, color: "#888", marginBottom: 16, fontWeight: 600, letterSpacing: 1 }}>SMS ALERTS</h3>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
          <div style={{ flex: 1 }}>
            <label style={label}>PHONE NUMBER</label>
            {editPhone ? (
              <div>
                <input style={input} placeholder="+1234567890" value={phoneForm.phone} onChange={e => setPhoneForm({ phone: e.target.value })} disabled={phoneStep === "sent"} />
                {phoneStep === "idle" && (
                  <div style={{ display: "flex", gap: 8 }}>
                    <button onClick={sendPhoneCode} disabled={loading} style={{ ...btnSecondary, background: "#111", color: "#fff", border: "none" }}>Send Code</button>
                    <button onClick={() => { setEditPhone(false); setPhoneStep("idle"); }} style={btnSecondary}>Cancel</button>
                  </div>
                )}
                {phoneStep === "sent" && (
                  <div>
                    <p style={{ color: "#888", fontSize: 12, marginBottom: 8 }}>Enter the 6-digit code sent to {phoneForm.phone}</p>
                    <input style={input} placeholder="123456" value={verifyCode} onChange={e => setVerifyCode(e.target.value)} maxLength={6} />
                    <div style={{ display: "flex", gap: 8 }}>
                      <button onClick={verifyPhone} disabled={loading} style={{ ...btnSecondary, background: "#111", color: "#fff", border: "none" }}>Verify</button>
                      <button onClick={() => setPhoneStep("idle")} style={btnSecondary}>Change number</button>
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                <p style={{ color: "#111", fontSize: 15, margin: 0 }}>{user.phone || "Not set"}</p>
                {user.phone && user.phone_verified && <span style={{ background: "#e6fff4", color: "#009950", padding: "2px 8px", borderRadius: 20, fontSize: 11 }}>✓ Verified</span>}
                {user.phone && !user.phone_verified && <span style={{ background: "#fff3e0", color: "#e65100", padding: "2px 8px", borderRadius: 20, fontSize: 11 }}>⚠ Not verified</span>}
              </div>
            )}
          </div>
          {!editPhone && <button onClick={() => { setEditPhone(true); setPhoneStep("idle"); }} style={{ ...btnSecondary, marginLeft: 12, marginTop: 18 }}>Edit</button>}
        </div>
      </div>

      {/* Password */}
      <div style={card}>
        <h3 style={{ fontSize: 13, color: "#888", marginBottom: 16, fontWeight: 600, letterSpacing: 1 }}>SECURITY</h3>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: changing ? 16 : 0 }}>
          <span style={{ color: "#111", fontWeight: 500 }}>Password</span>
          <button onClick={() => { setChanging(!changing); setMsg(null); }} style={btnSecondary}>{changing ? "Cancel" : "Change"}</button>
        </div>
        {changing && (
          <div>
            <label style={label}>CURRENT PASSWORD</label>
            <input style={input} type="password" value={form.current_password} onChange={e => setForm({ ...form, current_password: e.target.value })} />
            <label style={label}>NEW PASSWORD</label>
            <input style={input} type="password" value={form.new_password} onChange={e => setForm({ ...form, new_password: e.target.value })} />
            <label style={label}>CONFIRM PASSWORD</label>
            <input style={input} type="password" value={form.confirm} onChange={e => setForm({ ...form, confirm: e.target.value })} />
            <button onClick={changePassword} disabled={loading} style={btnPrimary}>{loading ? "Saving..." : "Save New Password"}</button>
          </div>
        )}
      </div>

      {/* Plan */}
      <div style={card}>
        <h3 style={{ fontSize: 13, color: "#888", marginBottom: 16, fontWeight: 600, letterSpacing: 1 }}>PLAN</h3>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <div>
            {user.plan === "premium" && <p style={{ color: "#111", fontSize: 15, margin: 0, fontWeight: 500 }}>⭐ Premium</p>}
            {user.plan === "pro" && <p style={{ color: "#111", fontSize: 15, margin: 0, fontWeight: 500 }}>🔥 Pro</p>}
            {(!user.plan || user.plan === "free") && <p style={{ color: "#111", fontSize: 15, margin: 0, fontWeight: 500 }}>Free</p>}
            {user.plan === "premium" && <p style={{ color: "#aaa", fontSize: 12, margin: "4px 0 0" }}>Unlimited cameras, zones, subject recognition</p>}
            {user.plan === "pro" && <p style={{ color: "#aaa", fontSize: 12, margin: "4px 0 0" }}>5 cameras, zones, alerts</p>}
            {(!user.plan || user.plan === "free") && <p style={{ color: "#aaa", fontSize: 12, margin: "4px 0 0" }}>1 camera, basic alerts</p>}
          </div>
          {(!user.plan || user.plan === "free") && <button style={{ ...btnSecondary, background: "#111", color: "#fff", border: "none" }}>Upgrade</button>}
          {user.plan === "pro" && <button style={{ ...btnSecondary, background: "#00cc66", color: "#fff", border: "none" }}>Upgrade to Premium</button>}
        </div>
      </div>


      {/* Enterprise */}
      <div style={{ background: "linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 100%)", border: "1px solid #333", borderRadius: 12, padding: 24, marginBottom: 12 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 12 }}>
          <span style={{ fontSize: 24 }}>🏢</span>
          <div>
            <h3 style={{ fontSize: 15, color: "#fff", margin: 0, fontWeight: 700 }}>Enterprise</h3>
            <p style={{ color: "#aaa", fontSize: 12, margin: 0 }}>40+ cameras · Custom pricing · White-glove setup</p>
          </div>
        </div>
        <div style={{ display: "flex", flexDirection: "column", gap: 6, marginBottom: 16 }}>
          {["Unlimited cameras across multiple locations", "AI subject recognition & named alerts", "Remote camera setup by our specialists", "DVR/NVR integration & migration", "Custom alerts & reporting", "Dedicated support & SLA"].map((f, i) => (
            <div key={i} style={{ display: "flex", alignItems: "center", gap: 8 }}>
              <span style={{ color: "#00cc66", fontSize: 14 }}>✓</span>
              <span style={{ color: "#ccc", fontSize: 13 }}>{f}</span>
            </div>
          ))}
        </div>
        <button
          onClick={() => { if (window.$crisp) { window.$crisp.push(["do", "chat:open"]); window.$crisp.push(["do", "message:send", ["text", "Hi, I am interested in Enterprise plan"]]); } }}
          style={{ background: "#00cc66", color: "#fff", border: "none", padding: "14px", borderRadius: 8, cursor: "pointer", fontWeight: 600, width: "100%", fontSize: 14 }}
        >
          Contact Sales →
        </button>
      </div>
      {/* Logout */}
      <button onClick={onLogout} style={{ background: "none", border: "1px solid #ddd", color: "#555", padding: "12px", borderRadius: 8, cursor: "pointer", width: "100%", fontSize: 14, marginBottom: 12 }}>Logout</button>

      {/* Delete account */}
      {!confirmDelete ? (
        <button onClick={() => setConfirmDelete(true)} style={{ background: "none", border: "none", color: "#ccc", padding: "8px", cursor: "pointer", width: "100%", fontSize: 12 }}>Delete account</button>
      ) : (
        <div style={{ background: "#fff0f0", border: "1px solid #ffcccc", borderRadius: 8, padding: 16 }}>
          <p style={{ color: "#cc0000", fontSize: 13, marginBottom: 12 }}>This will permanently delete your account and all cameras. Are you sure?</p>
          <div style={{ display: "flex", gap: 8 }}>
            <button onClick={deleteAccount} disabled={loading} style={{ background: "#cc0000", color: "#fff", border: "none", padding: "10px", borderRadius: 6, cursor: "pointer", flex: 1, fontSize: 13 }}>Yes, delete</button>
            <button onClick={() => setConfirmDelete(false)} style={{ ...btnSecondary, flex: 1 }}>Cancel</button>
          </div>
        </div>
      )}
    </div>
  );
}
