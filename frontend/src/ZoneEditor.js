import { useState, useEffect, useRef } from "react";
import api from "./api";

const BASE_COLS = 16;
const BASE_ROWS = 9;

export default function ZoneEditor({ camera, onBack }) {
  const [snapshot, setSnapshot] = useState(null);
  const [imgSize, setImgSize] = useState({ w: 16, h: 9 });
  const GRID_COLS = imgSize.w >= imgSize.h ? BASE_COLS : BASE_ROWS;
  const GRID_ROWS = imgSize.w >= imgSize.h ? BASE_ROWS : BASE_COLS;
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
    api.get("/cameras/" + camera.id + "/snapshot")
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

  const handleTouchStart = function(e, row, col) {
    e.preventDefault();
    setIsDragging(true);
    toggleCell(row, col);
  };

  const handleTouchMove = function(e) {
    e.preventDefault();
    const touch = e.touches[0];
    const el = document.elementFromPoint(touch.clientX, touch.clientY);
    if (el && el.dataset.row !== undefined) {
      const r = parseInt(el.dataset.row);
      const c = parseInt(el.dataset.col);
      const key = r + '_' + c;
      setSelectedCells(function(prev) {
        if (prev.indexOf(key) === -1) return [...prev, key];
        return prev;
      });
    }
  };

  const save = async function() {
    setSaving(true);
    const cells = selectedCells.map(function(k) {
      const parts = k.split("_");
      return [parseInt(parts[0]), parseInt(parts[1])];
    });
    await api.put("/cameras/" + camera.id + "/zone", { cells: cells });
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

      {loading && (
        <div style={{ textAlign: "center", padding: 60 }}>
          <div style={{
            width: 48, height: 48, border: "3px solid #1a1a1a",
            borderTop: "3px solid #00ff88", borderRadius: "50%",
            animation: "spin 0.8s linear infinite", margin: "0 auto 16px"
          }} />
          <p style={{ color: "#00ff88", fontSize: 14, fontWeight: 500 }}>Connecting to camera...</p>
          <p style={{ color: "#444", fontSize: 12, marginTop: 6 }}>Loading snapshot</p>
          <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
        </div>
      )}

      {!loading && !snapshot && (
        <div style={{ background: "#111", border: "1px solid #333", borderRadius: 12, padding: 40, textAlign: "center" }}>
          <p style={{ color: "#555", marginBottom: 16 }}>Could not connect to camera</p>
          <p style={{ color: "#333", fontSize: 12 }}>Draw zone on blank grid instead</p>
        </div>
      )}

      {!loading && (
        <div style={{ position: "relative", userSelect: "none", touchAction: "none" }} onMouseUp={handleMouseUp} onMouseLeave={handleMouseUp} onTouchMove={handleTouchMove} onTouchEnd={handleMouseUp}>
          {snapshot && (
            <img src={snapshot.image} alt="camera" style={{ width: "100%", borderRadius: 12, display: "block" }} onLoad={function(e) { setImgSize({ w: e.target.naturalWidth, h: e.target.naturalHeight }); }} />
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
                    onTouchStart={function(e) { handleTouchStart(e, row, col); }}
                    data-row={row}
                    data-col={col}
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
        <button onClick={clearAll} style={{ background: "#1a1a1a", color: "#fff", fontWeight: "bold", border: "1px solid #555", padding: "10px 20px", borderRadius: 8, cursor: "pointer", flex: 1 }}>Clear</button>
        <button onClick={selectAll} style={{ background: "#1a1a1a", color: "#fff", fontWeight: "bold", border: "1px solid #555", padding: "10px 20px", borderRadius: 8, cursor: "pointer", flex: 1 }}>Select All</button>
        <button onClick={save} disabled={saving} style={{ background: "#00ff88", color: "#000", border: "none", padding: "10px 20px", borderRadius: 8, cursor: "pointer", fontWeight: 500, flex: 2 }}>
          {saving ? "Saving..." : "Save Zone & Close"}
        </button>
      </div>
      <p style={{ color: "#333", fontSize: 12, marginTop: 12 }}>{selectedCells.length} cells selected</p>
    </div>
  );
}
