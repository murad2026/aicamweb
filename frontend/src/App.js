import { useState, useEffect } from "react";
import { requestPushPermission, onForegroundMessage } from "./usePush";
import api from "./api";
import AddCamera from "./AddCamera";
import Dashboard from "./Dashboard";

import Account from "./Account";
import Subjects from "./Subjects";
import Recognized from "./Recognized";

import Auth from "./Auth";
import ResetPassword from "./ResetPassword";
import "./App.css";

const savedUser = localStorage.getItem("user");
const initialUser = savedUser ? JSON.parse(savedUser) : null;
const urlParams = new URLSearchParams(window.location.search);
const resetToken = urlParams.get("token");

export default function App() {
  const [page, setPage] = useState("dashboard");
  const [refresh, setRefresh] = useState(0);
  const [user, setUser] = useState(initialUser);

  useEffect(function() {
    if (user) {
      requestPushPermission();
      // Refresh user data from server to get plan/cam_count
      api.get("/auth/me").then(r => {
        const updated = { ...user, ...r.data };
        console.log("auth/me response:", r.data);
        setUser(updated);
        localStorage.setItem("user", JSON.stringify(updated));
      }).catch(e => { console.log("auth/me error:", e); });
    }
  }, []);

  if (resetToken) {
    return <ResetPassword token={resetToken} onDone={function() { window.location.href = "/"; }} />;
  }

  const goBack = function() {
    setRefresh(function(r) { return r + 1; });
    setPage("dashboard");
  };

  const logout = function() {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    setUser(null);
  };

  const handleLogin = function(u) {
    setUser(u);
    localStorage.setItem("user", JSON.stringify(u));
  };

  if (!user) return <Auth onLogin={handleLogin} />;

  return (
    <div className="app">
      <header className="header">
        <div className="logo">
          <span className="logo-icon">⬡</span>
          <span className="logo-text">AI ANY CAMERA</span>
        </div>
        <nav>
          <button onClick={function() { setPage("dashboard"); }} className={page === "dashboard" ? "active" : ""}>Cameras</button>

          <button onClick={function() { setPage("subjects"); }} className={page === "subjects" ? "active" : ""} style={{ position: "relative" }}>
            Subjects
            {user?.new_subjects > 0 && <span style={{ position: "absolute", top: -6, right: -6, background: "#ff3366", color: "#fff", borderRadius: "50%", width: 16, height: 16, fontSize: 10, display: "flex", alignItems: "center", justifyContent: "center", fontWeight: 700 }}>{user.new_subjects}</span>}
          </button>
          <button onClick={function() { setPage("recognized"); }} className={page === "recognized" ? "active" : ""}>Recognized</button>
          <button onClick={function() { setPage("account"); }} className={page === "account" ? "active" : ""}>Account</button>
          <button onClick={function() { setPage("add"); }} className="btn-add">+ Add</button>
        </nav>
      </header>
      <main>
        {page === "dashboard" && <Dashboard key={refresh} onAdd={function() { setPage("add"); }} />}

        {page === "subjects" && <Subjects user={user} />}
        {page === "recognized" && <Recognized user={user} />}
        {page === "account" && <Account user={user} onLogout={logout} />}
        {page === "add" && <AddCamera onBack={goBack} user={user} />}
      </main>
      
    </div>
  );
}
