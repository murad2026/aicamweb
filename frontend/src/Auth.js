import { useState } from "react";
import api from "./api";

const FONT = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif";

export default function Auth({ onLogin }) {
  const [mode, setMode] = useState("login");
  const [form, setForm] = useState({ email: "", username: "", password: "" });
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const [forgotSent, setForgotSent] = useState(false);
  const [forgotMode, setForgotMode] = useState(false);
  const [openFaq, setOpenFaq] = useState(null);
  const [activeSegment, setActiveSegment] = useState(0);
  const [selectedBrand, setSelectedBrand] = useState(null);
  const [cameraRequest, setCameraRequest] = useState({ show: false, brand: "", model: "", email: "", sent: false });

  const input = {
    background: "#f5f5f5", border: "1px solid #e0e0e0", borderRadius: 10,
    padding: "14px 16px", color: "#111", fontSize: 15, width: "100%",
    fontFamily: FONT, outline: "none", marginBottom: 12, display: "block", boxSizing: "border-box"
  };
  const label = { fontSize: 12, color: "#999", marginBottom: 6, display: "block", letterSpacing: 0.5, fontFamily: FONT };
  const btn = { background: "#00cc66", color: "#fff", border: "none", padding: "14px", borderRadius: 10, cursor: "pointer", fontWeight: 700, width: "100%", fontSize: 15, fontFamily: FONT };

  const submit = async function() {
    setLoading(true); setError(null);
    try {
      const endpoint = mode === "login" ? "/auth/login" : "/auth/register";
      const r = await api.post(endpoint, form);
      localStorage.setItem("token", r.data.token);
      localStorage.setItem("user", JSON.stringify(r.data.user));
      onLogin(r.data.user);
    } catch(e) { setError(e.response?.data?.detail || (mode === 'login' ? 'Invalid email or password' : 'Registration failed. Email or username may already exist.')); }
    setLoading(false);
  };

  const sendForgot = async function() {
    if (!form.email) { setError("Enter your email"); return; }
    setLoading(true); setError(null);
    try {
      await api.post("/auth/forgot-password?email=" + encodeURIComponent(form.email));
      setForgotSent(true);
    } catch(e) { setError("Error sending reset email"); }
    setLoading(false);
  };

  const segments = [
    {
      icon: "🏪",
      label: "Retail & Restaurants",
      title: "Know what's happening in your business",
      subtitle: "when you're not on-site",
      desc: "AI Any Camera watches your store or restaurant 24/7, detects people and activity, and sends instant photo alerts — so you can catch theft, monitor staff, and protect your business.",
      points: [
        { icon: "🚨", title: "Theft & shoplifting alerts", desc: "Get notified the moment someone behaves suspiciously near your register, stockroom, or exit." },
        { icon: "👷", title: "After-hours monitoring", desc: "Know instantly if anyone enters your business outside of operating hours." },
        { icon: "📊", title: "Staff accountability", desc: "Monitor opening and closing procedures. Know who's on site and when." },
        { icon: "📸", title: "Incident documentation", desc: "Every alert comes with a photo. Perfect evidence for insurance or police reports." },
      ],
      ctaText: "Protect my business",
      pricingNote: "Less than $1/day — cheaper than one stolen item",
    },
    {
      icon: "🏠",
      label: "Airbnb & VRBO Hosts",
      title: "Know what's happening at your rental",
      subtitle: "when you're not there",
      desc: "AI Any Camera watches your property 24/7, detects people and activity, and sends instant photo alerts to your phone — so you can protect your rental before problems escalate.",
      points: [
        { icon: "🎉", title: "Party alerts", desc: "Get notified the moment a crowd shows up at your rental — not the next morning when the damage is done." },
        { icon: "🔐", title: "Unauthorized access", desc: "Know instantly if someone enters through a back door, garage, or area guests shouldn't be." },
        { icon: "🌙", title: "Late-night activity", desc: "Set quiet hour alerts. If guests are active at 2am, you'll know about it." },
        { icon: "🏘️", title: "Multiple properties", desc: "Monitor all your rentals from one dashboard. One alert system for your whole portfolio." },
      ],
      ctaText: "Protect my rental",
      pricingNote: "Less than $1/day to protect a rental earning $150+/night",
    },
    {
      icon: "🏢",
      label: "Property Managers",
      title: "One dashboard for all your properties",
      subtitle: "real-time alerts across every location",
      desc: "Manage security across your entire portfolio from a single account. Get instant alerts from any property, any camera — without paying for expensive enterprise systems.",
      points: [
        { icon: "🗺️", title: "All locations, one view", desc: "See the status of every camera across every property in one dashboard." },
        { icon: "⚡", title: "Instant alerts anywhere", desc: "Get photo alerts on your phone within seconds — no matter which property has activity." },
        { icon: "📋", title: "Event history per property", desc: "Review past events by location. Perfect for incident reports and tenant disputes." },
        { icon: "💰", title: "Scale without enterprise pricing", desc: "Pay only for the cameras you use. No contracts, no minimums, no per-site fees." },
      ],
      ctaText: "Set up my portfolio",
      pricingNote: "Add cameras one at a time as your portfolio grows",
    },
  ];

  const seg = segments[activeSegment];

  const steps = [
    { icon: "📷", title: "Connect your camera", desc: "Paste your RTSP link. Works with Unifi, Hikvision, Dahua, Reolink, Wyze and most IP cameras. Setup takes under 2 minutes." },
    { icon: "✏️", title: "Draw your detection zone", desc: "Select exactly which area triggers alerts — your entrance, register, or driveway. Everything outside is ignored." },
    { icon: "🚨", title: "Get instant alerts", desc: "AI detects people, cars, and animals. Photo alerts arrive in seconds via Email or SMS — wherever you are." },
  ];

  const faqs = [
    { q: "What types of businesses use this?", a: "Retail stores, restaurants, cafes, Airbnb rentals, VRBO properties, warehouses, and any small business with IP cameras." },
    { q: "What cameras are supported?", a: "Any camera with an RTSP stream — Unifi, Hikvision, Dahua, Reolink, Wyze v3 and most IP cameras." },
    { q: "Will I get false alerts from street traffic?", a: "No. You draw the detection zone only around your property. A car driving past won't trigger anything." },
    { q: "How smart is the detection?", a: "We use YOLO AI — it recognizes actual objects like people, cars, and dogs. Not shadows or light changes." },
    { q: "Is my footage private?", a: "Yes. Your camera feed is processed locally. Only alert snapshots are sent to your account — nobody else sees your footage." },
    { q: "How fast are alerts?", a: "Usually within 2–5 seconds of detection. Fast enough to call the police or a neighbor before a situation escalates." },
    { q: "Can I monitor multiple locations?", a: "Yes. Add as many cameras as you need across as many locations as you have. One account, one dashboard." },
  ];

  const cameraData = {
    "Unifi": [
      { name: "All models (G3, G4, G5, AI series)", supported: true, note: "Full support. Use RTSP from UniFi Protect settings." },
    ],
    "Hikvision": [
      { name: "All IP camera models", supported: true, note: "Full support. RTSP enabled by default." },
    ],
    "Dahua": [
      { name: "All IP camera models", supported: true, note: "Full support. RTSP enabled by default." },
    ],
    "Reolink": [
      { name: "E1, E1 Pro, RLC series", supported: true, note: "Full support. Enable RTSP in camera settings." },
      { name: "Argus (battery)", supported: false, note: "Not supported. Battery-powered cameras have no continuous stream." },
    ],
    "Wyze": [
      { name: "Cam v2", supported: true, note: "Supported. Install RTSP firmware from Wyze website first." },
      { name: "Cam v3", supported: true, note: "Supported. Enable RTSP in app: Settings → Advanced → RTSP." },
      { name: "Cam Pan v1 / v2", supported: true, note: "Supported. Enable RTSP in app settings." },
      { name: "Cam v4", supported: false, note: "Not supported. Wyze removed RTSP from v4." },
      { name: "Cam Pan v3", supported: false, note: "Not supported. No RTSP on Pan v3." },
      { name: "Cam Outdoor (battery)", supported: false, note: "Not supported. Battery cameras have no continuous stream." },
    ],
    "Axis": [
      { name: "All models", supported: true, note: "Full support. RTSP enabled by default." },
    ],
    "Amcrest": [
      { name: "All IP camera models", supported: true, note: "Full support. RTSP enabled by default." },
    ],
    "Lorex": [
      { name: "All wired IP cameras", supported: true, note: "Full support." },
      { name: "Battery/wireless models", supported: false, note: "Not supported. No RTSP stream." },
    ],
    "Ring": [
      { name: "All Ring cameras", supported: false, note: "Not supported. Ring uses proprietary cloud streaming, no RTSP." },
    ],
    "Nest / Google": [
      { name: "All Nest cameras", supported: false, note: "Not supported. Google removed RTSP access from Nest cameras." },
    ],
    "Blink": [
      { name: "All Blink cameras", supported: false, note: "Not supported. No RTSP available." },
    ],
    "Arlo": [
      { name: "Pro 3 / Pro 4 / Ultra", supported: null, note: "Partial support. Requires SmartHub and local network access." },
      { name: "All other Arlo models", supported: false, note: "Not supported. Cloud-only streaming." },
    ],
  };

  const supportedBrands = ["Unifi", "Hikvision", "Dahua", "Reolink", "Wyze", "Axis", "Amcrest", "Lorex"];
  const unsupportedBrands = ["Ring", "Nest / Google", "Blink", "Arlo"];

  return (
    <div style={{ background: "#ffffff", minHeight: "100vh", fontFamily: FONT }}>
      <style>{`
        @keyframes pulse { 0%,100%{box-shadow:0 0 0 0 rgba(0,204,102,0.3)} 50%{box-shadow:0 0 0 6px rgba(0,204,102,0)} }
        @keyframes fadeIn { from{opacity:0;transform:translateY(10px)} to{opacity:1;transform:translateY(0)} }
      `}</style>

      {/* Nav */}
      <nav style={{ padding: "20px 40px", display: "flex", justifyContent: "space-between", alignItems: "center", borderBottom: "1px solid #f0f0f0", background: "#fff", position: "sticky", top: 0, zIndex: 100 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <span style={{ color: "#00cc66", fontSize: 20 }}>⬡</span>
          <span style={{ color: "#111", fontSize: 15, fontWeight: 700, letterSpacing: 0.5 }}>AI Any Camera</span>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
          <a href="#compatibility" style={{
            display: "flex", alignItems: "center", gap: 6,
            background: "#f0fff8", border: "1px solid #00cc66",
            borderRadius: 20, padding: "7px 16px",
            color: "#00cc66", fontSize: 13, fontWeight: 600, textDecoration: "none",
            animation: "pulse 2s infinite"
          }}>
            <span style={{ width: 7, height: 7, borderRadius: "50%", background: "#00cc66", display: "inline-block" }}></span>
            Check Compatibility
          </a>
          <a href="https://t.me/aianycamera_bot" target="_blank" rel="noreferrer" style={{ color: "#999", fontSize: 14, textDecoration: "none" }}>Telegram Bot</a>
          <span style={{ background: "#f0fff8", border: "1px solid #00cc66", borderRadius: 20, padding: "6px 14px", color: "#00cc66", fontSize: 13, fontWeight: 600 }}>$29/mo per camera</span>
        </div>
      </nav>

      {/* Segment switcher */}
      <div style={{ display: "flex", justifyContent: "center", gap: 8, padding: "40px 24px 0", flexWrap: "wrap", background: "#fafafa", borderBottom: "1px solid #f0f0f0" }}>
        {segments.map((s, i) => (
          <button key={i} onClick={() => setActiveSegment(i)} style={{
            padding: "10px 20px", borderRadius: 20, cursor: "pointer", fontSize: 14, fontWeight: 600,
            background: activeSegment === i ? "#00cc66" : "#fff",
            color: activeSegment === i ? "#fff" : "#666",
            border: activeSegment === i ? "none" : "1px solid #e0e0e0",
            fontFamily: FONT, marginBottom: 16
          }}>{s.icon} {s.label}</button>
        ))}
      </div>

      {/* Hero */}
      <div style={{ display: "flex", flexDirection: "column", alignItems: "center", padding: "80px 24px 80px", background: "#fafafa" }}>
        <h1 style={{ color: "#111", fontSize: 52, fontWeight: 700, margin: "0 0 16px", textAlign: "center", lineHeight: 1.1, maxWidth: 900, letterSpacing: -1, whiteSpace: "nowrap" }}>
          Turn any camera into an AI alert system.<br/><span style={{ color: "#00cc66" }}>Instant text, every time.</span>
        </h1>
        <p style={{ color: "#888", fontSize: 20, textAlign: "center", maxWidth: 580, marginBottom: 56, lineHeight: 1.6 }}>
          AI Any Camera watches your property 24/7, detects people and activity, and sends an immediate text message with a photo — so you can act before problems escalate.
        </p>

        {/* Auth form */}
        <div style={{ width: "100%", maxWidth: 420, background: "#fff", borderRadius: 20, border: "1px solid #e8e8e8", padding: 32, boxShadow: "0 4px 24px rgba(0,0,0,0.06)" }}>
          <div style={{ display: "flex", gap: 8, marginBottom: 28, background: "#f5f5f5", borderRadius: 10, padding: 4 }}>
            <button onClick={() => setMode("login")} style={{ flex: 1, padding: "10px", borderRadius: 8, cursor: "pointer", fontWeight: 600, fontSize: 14, background: mode === "login" ? "#fff" : "transparent", color: mode === "login" ? "#111" : "#999", border: "none", fontFamily: FONT, boxShadow: mode === "login" ? "0 1px 4px rgba(0,0,0,0.1)" : "none" }}>Sign in</button>
            <button onClick={() => setMode("register")} style={{ flex: 1, padding: "10px", borderRadius: 8, cursor: "pointer", fontWeight: 700, fontSize: 14, background: mode === "register" ? "#00cc66" : "transparent", color: mode === "register" ? "#fff" : "#00cc66", border: "none", fontFamily: FONT }}>Try it free</button>
          </div>

          <label style={label}>EMAIL</label>
          <input style={input} placeholder="you@example.com" value={form.email} onChange={e => setForm({ ...form, email: e.target.value })} />

          {mode === "register" && <>
            <label style={label}>USERNAME</label>
            <input style={input} placeholder="username" value={form.username} onChange={e => setForm({ ...form, username: e.target.value })} />
          </>}

          {!forgotMode && <>
            <label style={label}>PASSWORD</label>
            <input style={input} type="password" placeholder="••••••••" value={form.password} onChange={e => setForm({ ...form, password: e.target.value })} onKeyDown={e => e.key === "Enter" && submit()} />
          </>}

          {error && <p style={{ color: "#ff4466", fontSize: 13, marginBottom: 12, fontFamily: FONT }}>{error}</p>}

          {!forgotMode && <button onClick={submit} disabled={loading} style={btn}>{loading ? "..." : mode === "login" ? "Sign in" : seg.ctaText}</button>}

          {forgotMode && !forgotSent && <div>
            <button onClick={sendForgot} disabled={loading} style={btn}>{loading ? "Sending..." : "Send reset link"}</button>
            <p style={{ textAlign: "center", marginTop: 12 }}><span onClick={() => setForgotMode(false)} style={{ color: "#999", fontSize: 13, cursor: "pointer", fontFamily: FONT }}>Back to sign in</span></p>
          </div>}

          {mode === "login" && !forgotSent && !forgotMode && (
            <p style={{ textAlign: "center", marginTop: 16 }}><span onClick={() => setForgotMode(true)} style={{ color: "#999", fontSize: 13, cursor: "pointer", fontFamily: FONT }}>Forgot password?</span></p>
          )}

          {forgotSent && <p style={{ textAlign: "center", marginTop: 16, color: "#00cc66", fontSize: 13, fontFamily: FONT }}>✓ Reset link sent to {form.email}</p>}
        </div>

        <p style={{ color: "#bbb", fontSize: 13, marginTop: 20 }}>No credit card required · Cancel anytime</p>
      </div>

      {/* Pain points */}
      <div style={{ padding: "80px 24px", maxWidth: 960, margin: "0 auto" }}>
        <p style={{ color: "#00cc66", fontSize: 13, fontWeight: 600, textAlign: "center", marginBottom: 12, letterSpacing: 1 }}>WHY PEOPLE USE IT</p>
        <h2 style={{ color: "#111", fontSize: 36, fontWeight: 700, textAlign: "center", marginBottom: 56, letterSpacing: -0.5 }}>Stop finding out too late</h2>
        <div style={{ display: "flex", gap: 20, flexWrap: "wrap", justifyContent: "center" }}>
          {seg.points.map((p, i) => (
            <div key={i} style={{ flex: 1, minWidth: 200, background: "#fff", border: "1px solid #f0f0f0", borderRadius: 20, padding: 28, boxShadow: "0 2px 12px rgba(0,0,0,0.04)" }}>
              <div style={{ fontSize: 28, marginBottom: 16 }}>{p.icon}</div>
              <h3 style={{ color: "#111", fontSize: 17, fontWeight: 600, marginBottom: 10, lineHeight: 1.3 }}>{p.title}</h3>
              <p style={{ color: "#888", fontSize: 14, lineHeight: 1.7, margin: 0 }}>{p.desc}</p>
            </div>
          ))}
        </div>
      </div>

      {/* How it works */}
      <div style={{ padding: "80px 24px", maxWidth: 960, margin: "0 auto", background: "#fafafa", borderRadius: 32 }}>
        <p style={{ color: "#00cc66", fontSize: 13, fontWeight: 600, textAlign: "center", marginBottom: 12, letterSpacing: 1 }}>HOW IT WORKS</p>
        <h2 style={{ color: "#111", fontSize: 36, fontWeight: 700, textAlign: "center", marginBottom: 56, letterSpacing: -0.5 }}>Set up in 2 minutes</h2>
        <div style={{ display: "flex", gap: 20, flexWrap: "wrap", justifyContent: "center" }}>
          {steps.map((s, i) => (
            <div key={i} style={{ flex: 1, minWidth: 240, background: "#fff", border: "1px solid #f0f0f0", borderRadius: 20, padding: 32, boxShadow: "0 2px 12px rgba(0,0,0,0.04)" }}>
              <div style={{ fontSize: 28, marginBottom: 20 }}>{s.icon}</div>
              <div style={{ color: "#00cc66", fontSize: 12, fontWeight: 700, marginBottom: 10, letterSpacing: 1 }}>0{i+1}</div>
              <h3 style={{ color: "#111", fontSize: 18, fontWeight: 600, marginBottom: 10, lineHeight: 1.3 }}>{s.title}</h3>
              <p style={{ color: "#888", fontSize: 15, lineHeight: 1.7, margin: 0 }}>{s.desc}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Camera Compatibility Checker */}
      <div id="compatibility" style={{ padding: "80px 24px", maxWidth: 760, margin: "0 auto" }}>
        <p style={{ color: "#00cc66", fontSize: 13, fontWeight: 600, textAlign: "center", marginBottom: 12, letterSpacing: 1 }}>COMPATIBILITY CHECKER</p>
        <h2 style={{ color: "#111", fontSize: 36, fontWeight: 700, textAlign: "center", marginBottom: 16, letterSpacing: -0.5 }}>Does your camera work?</h2>
        <p style={{ color: "#888", fontSize: 16, textAlign: "center", marginBottom: 48 }}>Select your camera brand to check compatibility</p>

        <div style={{ marginBottom: 24 }}>
          <p style={{ color: "#bbb", fontSize: 12, fontWeight: 600, letterSpacing: 1, marginBottom: 12 }}>SUPPORTED BRANDS</p>
          <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
            {supportedBrands.map(brand => (
              <button key={brand} onClick={() => setSelectedBrand(brand)} style={{
                padding: "10px 16px", borderRadius: 12, cursor: "pointer", fontSize: 14, fontWeight: 600,
                background: selectedBrand === brand ? "#00cc66" : "#fff",
                color: selectedBrand === brand ? "#fff" : "#555",
                border: selectedBrand === brand ? "none" : "1px solid #e0e0e0",
                fontFamily: FONT
              }}>{brand}</button>
            ))}
          </div>
        </div>

        <div style={{ marginBottom: 40 }}>
          <p style={{ color: "#bbb", fontSize: 12, fontWeight: 600, letterSpacing: 1, marginBottom: 12 }}>CLOUD-ONLY (NOT SUPPORTED)</p>
          <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
            {unsupportedBrands.map(brand => (
              <button key={brand} onClick={() => setSelectedBrand(brand)} style={{
                padding: "10px 16px", borderRadius: 12, cursor: "pointer", fontSize: 14, fontWeight: 500,
                background: selectedBrand === brand ? "#fff0f0" : "#fff",
                color: selectedBrand === brand ? "#ff4466" : "#bbb",
                border: selectedBrand === brand ? "1px solid #ff4466" : "1px solid #e0e0e0",
                fontFamily: FONT
              }}>{brand}</button>
            ))}
          </div>
        </div>

        {selectedBrand && (
          <div style={{ background: "#fff", border: "1px solid #e8e8e8", borderRadius: 20, padding: 32, boxShadow: "0 2px 12px rgba(0,0,0,0.04)", animation: "fadeIn 0.3s ease" }}>
            <h3 style={{ color: "#111", fontSize: 20, fontWeight: 700, marginBottom: 24 }}>{selectedBrand}</h3>
            <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
              {cameraData[selectedBrand].map((model, i) => (
                <div key={i} style={{
                  display: "flex", alignItems: "flex-start", gap: 16, padding: 16,
                  background: model.supported === true ? "#f0fff8" : model.supported === false ? "#fff5f5" : "#fffdf0",
                  borderRadius: 12,
                  border: `1px solid ${model.supported === true ? "#c3f0d8" : model.supported === false ? "#ffd0d8" : "#ffe8a0"}`
                }}>
                  <span style={{ fontSize: 20, flexShrink: 0 }}>
                    {model.supported === true ? "✅" : model.supported === false ? "❌" : "⚠️"}
                  </span>
                  <div>
                    <p style={{ color: "#111", fontSize: 15, fontWeight: 600, margin: "0 0 4px" }}>{model.name}</p>
                    <p style={{ color: model.supported === true ? "#00aa55" : model.supported === false ? "#cc2244" : "#aa7700", fontSize: 13, margin: 0 }}>{model.note}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* My brand isn't listed */}
        <div style={{ marginTop: 32, textAlign: "center" }}>
          {!cameraRequest.show && !cameraRequest.sent && (
            <button onClick={() => setCameraRequest({ ...cameraRequest, show: true })} style={{
              background: "#fff", border: "1px solid #e0e0e0", borderRadius: 12,
              padding: "12px 24px", color: "#888", fontSize: 14, cursor: "pointer", fontFamily: FONT
            }}>
              🔍 My camera brand isn't listed — request support
            </button>
          )}

          {cameraRequest.show && !cameraRequest.sent && (
            <div style={{ background: "#fff", border: "1px solid #e8e8e8", borderRadius: 20, padding: 32, textAlign: "left", marginTop: 16, boxShadow: "0 2px 12px rgba(0,0,0,0.04)" }}>
              <h3 style={{ color: "#111", fontSize: 18, fontWeight: 700, marginBottom: 8 }}>Request camera support</h3>
              <p style={{ color: "#888", fontSize: 14, marginBottom: 24 }}>Tell us your camera model and we'll check if we can add support.</p>
              <label style={label}>CAMERA BRAND</label>
              <input style={input} placeholder="e.g. Eufy, Tapo, Nest..." value={cameraRequest.brand} onChange={e => setCameraRequest({ ...cameraRequest, brand: e.target.value })} />
              <label style={label}>CAMERA MODEL</label>
              <input style={input} placeholder="e.g. EufyCam 2C, Tapo C200..." value={cameraRequest.model} onChange={e => setCameraRequest({ ...cameraRequest, model: e.target.value })} />
              <label style={label}>YOUR EMAIL (optional)</label>
              <input style={input} placeholder="we'll notify you when supported" value={cameraRequest.email} onChange={e => setCameraRequest({ ...cameraRequest, email: e.target.value })} />
              <button onClick={async () => {
                if (!cameraRequest.brand || !cameraRequest.model) return;
                try { await api.post("/camera-request", { brand: cameraRequest.brand, model: cameraRequest.model, email: cameraRequest.email }); } catch(e) {}
                setCameraRequest({ ...cameraRequest, sent: true, show: false });
              }} style={btn}>Submit request</button>
            </div>
          )}

          {cameraRequest.sent && (
            <div style={{ background: "#f0fff8", border: "1px solid #c3f0d8", borderRadius: 16, padding: 24, marginTop: 16 }}>
              <p style={{ color: "#00aa55", fontSize: 16, fontWeight: 600, margin: "0 0 8px" }}>✓ Request received!</p>
              <p style={{ color: "#888", fontSize: 14, margin: 0 }}>We'll check if {cameraRequest.brand} {cameraRequest.model} supports RTSP and notify you.</p>
            </div>
          )}
        </div>
      </div>

      {/* Pricing */}
      <div style={{ padding: "80px 24px", maxWidth: 480, margin: "0 auto", textAlign: "center" }}>
        <p style={{ color: "#00cc66", fontSize: 13, fontWeight: 600, marginBottom: 12, letterSpacing: 1 }}>PRICING</p>
        <h2 style={{ color: "#111", fontSize: 36, fontWeight: 700, marginBottom: 40, letterSpacing: -0.5 }}>Simple, honest pricing</h2>
        <div style={{ background: "#fff", border: "1px solid #e8e8e8", borderRadius: 24, padding: 40, boxShadow: "0 4px 24px rgba(0,204,102,0.1)" }}>
          <p style={{ color: "#999", fontSize: 14, marginBottom: 8 }}>AI Protection Plan</p>
          <div style={{ display: "flex", alignItems: "baseline", justifyContent: "center", gap: 4, marginBottom: 8 }}>
            <span style={{ color: "#00cc66", fontSize: 52, fontWeight: 700 }}>$29</span>
            <span style={{ color: "#999", fontSize: 16 }}>/month per camera</span>
          </div>
          <p style={{ color: "#bbb", fontSize: 13, marginBottom: 32 }}>{seg.pricingNote}</p>
          <div style={{ textAlign: "left", marginBottom: 32 }}>
            {["✓ 24/7 AI monitoring", "✓ Instant photo alerts via Email & SMS", "✓ Custom detection zones", "✓ People, car & animal detection", "✓ Event history & recordings", "✓ Works with any IP camera", "✓ Cancel anytime"].map((f, i) => (
              <p key={i} style={{ color: "#555", fontSize: 15, margin: "0 0 12px", fontFamily: FONT }}>{f}</p>
            ))}
          </div>
          <button onClick={() => setMode("register")} style={btn}>Start free trial</button>
        </div>
      </div>

      {/* Video */}
      <div style={{ padding: "0 24px 80px", maxWidth: 960, margin: "0 auto" }}>
        <p style={{ color: "#00cc66", fontSize: 13, fontWeight: 600, textAlign: "center", marginBottom: 12, letterSpacing: 1 }}>DEMO</p>
        <h2 style={{ color: "#111", fontSize: 36, fontWeight: 700, textAlign: "center", marginBottom: 40, letterSpacing: -0.5 }}>See it in action</h2>
        <div style={{ background: "#f5f5f5", border: "1px solid #e8e8e8", borderRadius: 20, height: 400, display: "flex", alignItems: "center", justifyContent: "center", flexDirection: "column", gap: 16 }}>
          <div style={{ width: 64, height: 64, background: "#e8e8e8", borderRadius: "50%", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 24 }}>▶</div>
          <p style={{ color: "#bbb", fontSize: 15 }}>Video coming soon</p>
        </div>
      </div>

      {/* FAQ */}
      <div style={{ padding: "0 24px 80px", maxWidth: 680, margin: "0 auto" }}>
        <p style={{ color: "#00cc66", fontSize: 13, fontWeight: 600, textAlign: "center", marginBottom: 12, letterSpacing: 1 }}>FAQ</p>
        <h2 style={{ color: "#111", fontSize: 36, fontWeight: 700, textAlign: "center", marginBottom: 48, letterSpacing: -0.5 }}>Common questions</h2>
        {faqs.map((f, i) => (
          <div key={i} style={{ borderBottom: "1px solid #f0f0f0", padding: "20px 0", cursor: "pointer" }} onClick={() => setOpenFaq(openFaq === i ? null : i)}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <p style={{ color: "#111", fontSize: 16, margin: 0, fontWeight: 500 }}>{f.q}</p>
              <span style={{ color: "#bbb", fontSize: 20, marginLeft: 16 }}>{openFaq === i ? "−" : "+"}</span>
            </div>
            {openFaq === i && <p style={{ color: "#888", fontSize: 15, marginTop: 14, marginBottom: 0, lineHeight: 1.7 }}>{f.a}</p>}
          </div>
        ))}
      </div>

      {/* CTA */}
      <div style={{ padding: "80px 24px", textAlign: "center", background: "#fafafa", borderTop: "1px solid #f0f0f0" }}>
        <h2 style={{ color: "#111", fontSize: 40, fontWeight: 700, marginBottom: 16, letterSpacing: -0.5 }}>Ready to protect what matters?</h2>
        <p style={{ color: "#888", fontSize: 18, marginBottom: 40 }}>Join businesses and property owners who sleep better knowing their cameras are working for them.</p>
        <button onClick={() => { setMode("register"); window.scrollTo({ top: 0, behavior: "smooth" }); }} style={{ ...btn, width: "auto", padding: "16px 40px", fontSize: 16 }}>Get started free →</button>
      </div>

      {/* Footer */}
      <div style={{ borderTop: "1px solid #f0f0f0", padding: "32px 24px", display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 16 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <span style={{ color: "#00cc66", fontSize: 16 }}>⬡</span>
          <span style={{ color: "#999", fontSize: 14 }}>AI Any Camera</span>
        </div>
        <div style={{ display: "flex", gap: 24 }}>
          <a href="https://murad2026.github.io/aicamweb/privacy.html" target="_blank" rel="noreferrer" style={{ color: "#bbb", fontSize: 13, textDecoration: "none" }}>Privacy</a>
          <a href="https://murad2026.github.io/aicamweb/terms.html" target="_blank" rel="noreferrer" style={{ color: "#bbb", fontSize: 13, textDecoration: "none" }}>Terms</a>
          <a href="mailto:hello@aianycamera.com" style={{ color: "#bbb", fontSize: 13, textDecoration: "none" }}>Contact</a>
        </div>
        <p style={{ color: "#ddd", fontSize: 13, margin: 0 }}>© 2026 AI Any Camera</p>
      </div>

    </div>
  );
}
