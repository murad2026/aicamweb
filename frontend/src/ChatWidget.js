import { useState, useRef, useEffect } from "react";
import api from "./api";

const HUMAN_TRIGGERS = ["talk to human", "talk to agent", "real person", "speak to someone", "human agent", "live agent", "live chat", "talk to someone", "speak with", "contact sales", "sales team"];

export default function ChatWidget({ user }) {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState([
    { role: "assistant", content: "Hi! I'm your AI Any Camera assistant. Ask me anything about connecting cameras, setting up alerts, or our plans. You can also type 'talk to human' to connect with our team." }
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [escalated, setEscalated] = useState(false);
  const bottomRef = useRef(null);

  useEffect(() => {
    if (open) bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, open]);

  const isHumanRequest = (text) => {
    const lower = text.toLowerCase();
    return HUMAN_TRIGGERS.some(trigger => lower.includes(trigger));
  };

  const escalateToHuman = async (lastMessage) => {
    setEscalated(true);
    try {
      await api.post("/chat/escalate", { last_message: lastMessage });
    } catch(e) {
      console.error("Escalation error:", e);
    }
    setMessages(prev => [...prev, {
      role: "assistant",
      content: "I'm connecting you with our team now. 🙋 We'll reach out to you shortly via email or phone. In the meantime, feel free to keep chatting!",
      isEscalation: true
    }]);
  };

  const send = async () => {
    if (!input.trim() || loading) return;
    const userText = input.trim();
    const userMsg = { role: "user", content: userText };
    const newMessages = [...messages, userMsg];
    setMessages(newMessages);
    setInput("");
    setLoading(true);

    // Check if user wants human
    if (isHumanRequest(userText) && !escalated) {
      setLoading(false);
      await escalateToHuman(userText);
      return;
    }

    try {
      const apiMessages = newMessages
        .filter((m, i) => !(m.role === "assistant" && i === 0))
        .filter(m => !m.isEscalation)
        .map(m => ({ role: m.role, content: m.content }));

      const r = await api.post("/chat", { messages: apiMessages });
      const reply = r.data.reply;

      // Check if AI reply suggests human escalation
      const shouldEscalate = !escalated && (
        reply.toLowerCase().includes("contact our team") ||
        reply.toLowerCase().includes("speak with a human") ||
        reply.toLowerCase().includes("talk to someone")
      );

      setMessages([...newMessages, { role: "assistant", content: reply }]);

      if (shouldEscalate) {
        setTimeout(() => escalateToHuman(userText), 1000);
      }
    } catch(e) {
      setMessages([...newMessages, { role: "assistant", content: "Sorry, I'm having trouble responding. Please try again." }]);
    }
    setLoading(false);
  };

  const handleTalkToHuman = async () => {
    if (escalated) return;
    setMessages(prev => [...prev, { role: "user", content: "I'd like to talk to a human agent." }]);
    await escalateToHuman("Clicked Talk to Human button");
  };

  return (
    <>
      {/* Chat button */}
      <button onClick={() => setOpen(!open)} style={{
        position: "fixed", bottom: 24, right: 24, width: 52, height: 52,
        borderRadius: "50%", background: "#111", border: "none", cursor: "pointer",
        display: "flex", alignItems: "center", justifyContent: "center",
        boxShadow: "0 4px 16px rgba(0,0,0,0.2)", zIndex: 999, fontSize: 22
      }}>
        {open ? "✕" : "💬"}
      </button>

      {/* Chat window */}
      {open && (
        <div style={{
          position: "fixed", bottom: 88, right: 24, width: 340, height: 500,
          background: "#fff", borderRadius: 16, boxShadow: "0 8px 32px rgba(0,0,0,0.15)",
          display: "flex", flexDirection: "column", zIndex: 999, overflow: "hidden",
          border: "1px solid #e0e0e0"
        }}>
          {/* Header */}
          <div style={{ background: "#111", padding: "14px 16px", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
            <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
              <div style={{ width: 32, height: 32, borderRadius: "50%", background: "#00cc66", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 16 }}>⬡</div>
              <div>
                <p style={{ color: "#fff", fontSize: 14, fontWeight: 600, margin: 0 }}>
                  {escalated ? "Our Team" : "AI Assistant"}
                </p>
                <p style={{ color: "#aaa", fontSize: 11, margin: 0 }}>
                  {escalated ? "🟢 Team notified" : "Always here to help"}
                </p>
              </div>
            </div>
            {/* Talk to human button */}
            {!escalated && (
              <button onClick={handleTalkToHuman} style={{
                background: "rgba(255,255,255,0.1)", border: "1px solid rgba(255,255,255,0.2)",
                color: "#fff", borderRadius: 20, padding: "4px 10px",
                cursor: "pointer", fontSize: 11, whiteSpace: "nowrap"
              }}>👤 Human</button>
            )}
            {escalated && (
              <span style={{
                background: "#00cc66", color: "#fff", borderRadius: 20,
                padding: "4px 10px", fontSize: 11
              }}>✓ Notified</span>
            )}
          </div>

          {/* Messages */}
          <div style={{ flex: 1, overflowY: "auto", padding: 16, display: "flex", flexDirection: "column", gap: 10 }}>
            {messages.map((m, i) => (
              <div key={i} style={{ display: "flex", justifyContent: m.role === "user" ? "flex-end" : "flex-start" }}>
                <div style={{
                  maxWidth: "80%", padding: "10px 14px",
                  borderRadius: m.role === "user" ? "16px 16px 4px 16px" : "16px 16px 16px 4px",
                  background: m.isEscalation ? "#e6fff4" : m.role === "user" ? "#111" : "#f5f5f7",
                  border: m.isEscalation ? "1px solid #00cc66" : "none",
                  color: m.role === "user" ? "#fff" : "#111",
                  fontSize: 13, lineHeight: 1.5
                }}>{m.content}</div>
              </div>
            ))}
            {loading && (
              <div style={{ display: "flex", justifyContent: "flex-start" }}>
                <div style={{ background: "#f5f5f7", borderRadius: "16px 16px 16px 4px", padding: "10px 14px", fontSize: 13, color: "#888" }}>Thinking...</div>
              </div>
            )}
            <div ref={bottomRef} />
          </div>

          {/* Quick replies */}
          {messages.length === 1 && (
            <div style={{ padding: "0 16px 8px", display: "flex", flexWrap: "wrap", gap: 6 }}>
              {["Pricing", "Connect a camera", "Talk to human"].map(q => (
                <button key={q} onClick={() => { setInput(q); }} style={{
                  background: "#f5f5f7", border: "none", borderRadius: 20,
                  padding: "6px 12px", cursor: "pointer", fontSize: 12, color: "#555"
                }}>{q}</button>
              ))}
            </div>
          )}

          {/* Input */}
          <div style={{ padding: "12px 16px", borderTop: "1px solid #eee", display: "flex", gap: 8 }}>
            <input
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={e => e.key === "Enter" && send()}
              placeholder={escalated ? "Our team will reach out soon..." : "Ask anything..."}
              style={{ flex: 1, background: "#f5f5f7", border: "none", borderRadius: 20, padding: "10px 14px", fontSize: 13, outline: "none", color: "#111" }}
            />
            <button onClick={send} disabled={loading || !input.trim()} style={{
              background: "#111", border: "none", borderRadius: "50%", width: 36, height: 36,
              cursor: "pointer", color: "#fff", fontSize: 16, display: "flex", alignItems: "center", justifyContent: "center",
              opacity: (!input.trim() || loading) ? 0.5 : 1
            }}>→</button>
          </div>
        </div>
      )}
    </>
  );
}
