import { useState, useEffect, useRef } from "react";
import api from "./api";

const GRID_COLS = 16;
const GRID_ROWS = 9;

export default function ZoneEditor({ camera, onBack }) {
  const [snapshot, setSnapshot] = useState(null);
  const [selectedCells, setSelectedCells] = useState(function() {
    if (camera.zone && camera.zone.cells) {
      return camera.zone.cells.map(function(c) { return c[0] + "_" + c[1]; });
    }
    return [];
  });
  const [isDragging, setIsDragging] = useState(false);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(function() {
    api.get("https://b48a-108-26-229-43.ngrok-free.app/cameras/" + camera.id + "/snapshot")
      .then(function(r) {
        setSnapshot(r.data);
        setLoading(false);
      })
      .catch(function() {
        setLoading(false);
      });
  }, [camera.id]);

  const toggleCell = function(row, col) {
    const key = row + "_" + col;
    setSelectedCells(function(prev) {
      if (prev.includes(key)) return prev.filter(function(c) { return c !== key; });
      return [...prev, key];
    });
  };

  const handleMouseDown = function(row, col) {
    setIsDragging(true);
    toggleCell(row, col);
  };

  const handleMouseEnter = function(row, col) {
    if (isDragging) toggleCell(row, col);
  };

  const handleMouseUp = function() {
    setIsDragging(false);
  };

  const save = async function() {
    setSaving(true);
    const cells = selectedCells.map(function(k) {
      const parts = k.split("_");
      return [parseInt(parts[0]), parseInt(parts[1])];
    });
    await api.put("https://b48a-108-26-229-43.ngrok-free.app/cameras/" + camera.id + "/zone", { cells: cells });
    setSaving(false);
    onBack();
  };

  const clearAll = function() { setSelectedCells([]); };
  const selectAll = function() {
    const all = [];
    for (let r = 0; r < GRID_ROWS; r++) {
      for (let c = 0; c < GRID_COLS; c++) {
        all.push(r + "_" + c);
      }
    }
    setSelectedCells(all);
  };

  return (
    <div style={{ maxWidth: 900 }}>
      <button onClick={onBack} style={{ background: "none", border: "none", color: "#555", cursor: "pointer", marginBottom: 24, fontFamily: "sans-serif" }}>← Back</button>
      <h2 style={{ fontSize: 24, marginBottom: 8, color: "#f0f0f0", fontFamily: "monospace" }}>Draw Alert Zone</h2>
      <p style={{ color: "#555", marginBottom: 24, fontSize: 14 }}>Click or drag to select cells where alerts should trigger</p>

      {loading && <p style={{ color: "#555" }}>Loading snapshot from camera...</p>}

      {!loading && !snapshot && (
        <div style={{ background: "#111", border: "1px solid #333", borderRadius: 12, padding: 40, textAlign: "center" }}>
          <p style={{ color: "#555", marginBottom: 16 }}>Could not connect to camera</p>
          <p style={{ color: "#333", fontSize: 12 }}>Draw zone on blank grid instead</p>
        </div>
      )}

      {!loading && (
        <div style={{ position: "relative", userSelect: "none" }} onMouseUp={handleMouseUp} onMouseLeave={handleMouseUp}>
          {snapshot && (
            <img src={snapshot.image} alt="camera" style={{ width: "100%", borderRadius: 12, display: "block" }} />
          )}
          {!snapshot && (
            <div style={{ width: "100%", paddingTop: "56.25%", background: "#0a0a0a", borderRadius: 12, border: "1px solid #222" }} />
          )}
          <div style={{
            position: "absolute", top: 0, left: 0, right: 0, bottom: 0,
            display: "grid",
            gridTemplateColumns: "repeat(" + GRID_COLS + ", 1fr)",
            gridTemplateRows: "repeat(" + GRID_ROWS + ", 1fr)",
            borderRadius: 12, overflow: "hidden"
          }}>
            {Array.from({ length: GRID_ROWS }).map(function(_, row) {
              return Array.from({ length: GRID_COLS }).map(function(_, col) {
                const key = row + "_" + col;
                const isSelected = selectedCells.includes(key);
                return (
                  <div key={key}
                    onMouseDown={function() { handleMouseDown(row, col); }}
                    onMouseEnter={function() { handleMouseEnter(row, col); }}
                    style={{
                      border: "1px solid rgba(255,255,255,0.05)",
                      background: isSelected ? "rgba(0,255,136,0.35)" : "rgba(0,0,0,0.01)",
                      cursor: "pointer",
                      transition: "background 0.1s"
                    }}
                  />
                );
              });
            })}
          </div>
        </div>
      )}

      <div style={{ display: "flex", gap: 12, marginTop: 20 }}>
        <button onClick={clearAll} style={{ background: "#1a1a1a", color: "#666", border: "1px solid #333", padding: "10px 20px", borderRadius: 8, cursor: "pointer", flex: 1 }}>Clear</button>
        <button onClick={selectAll} style={{ background: "#1a1a1a", color: "#666", border: "1px solid #333", padding: "10px 20px", borderRadius: 8, cursor: "pointer", flex: 1 }}>Select All</button>
        <button onClick={save} disabled={saving} style={{ background: "#00ff88", color: "#000", border: "none", padding: "10px 20px", borderRadius: 8, cursor: "pointer", fontWeight: 500, flex: 2 }}>
          {saving ? "Saving..." : "Save Zone ✓"}
        </button>
      </div>
      <p style={{ color: "#333", fontSize: 12, marginTop: 12 }}>{selectedCells.length} cells selected</p>
    </div>
  );
}
