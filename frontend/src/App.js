import { useState } from "react";
import AddCamera from "./AddCamera";
import Dashboard from "./Dashboard";
import Events from "./Events";
import Account from "./Account";
import Auth from "./Auth";
import "./App.css";

const savedUser = localStorage.getItem("user");
const initialUser = savedUser ? JSON.parse(savedUser) : null;

export default function App() {
  const [page, setPage] = useState("dashboard");
  const [refresh, setRefresh] = useState(0);
  const [user, setUser] = useState(initialUser);

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
          <button onClick={function() { setPage("events"); }} className={page === "events" ? "active" : ""}>Events</button>
          <button onClick={function() { setPage("account"); }} className={page === "account" ? "active" : ""}>Account</button>
          <button onClick={function() { setPage("add"); }} className="btn-add">+ Add</button>
        </nav>
      </header>
      <main>
        {page === "dashboard" && <Dashboard key={refresh} onAdd={function() { setPage("add"); }} />}
        {page === "events" && <Events />}
        {page === "account" && <Account user={user} onLogout={logout} />}
        {page === "add" && <AddCamera onBack={goBack} />}
      </main>
    </div>
  );
}
