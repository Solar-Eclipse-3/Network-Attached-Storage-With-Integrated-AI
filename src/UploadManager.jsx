import React, { useState, useRef } from "react";

const API_BASE = import.meta.env.VITE_API_BASE ?? "/api";
const UPLOAD_KEY = import.meta.env.VITE_UPLOAD_KEY ?? null;
const joinApiRoute = (path = "") => {
  const normalizedPath = path.startsWith("/") ? path : `/${path}`;
  const base = API_BASE.endsWith("/") ? API_BASE.slice(0, -1) : API_BASE;
  return `${base}${normalizedPath}`;
};

function isImage(file) {
  return file.type.startsWith("image/");
}

export default function UploadManager({ onUploaded }) {
  const [items, setItems] = useState([]);
  const [isDragging, setIsDragging] = useState(false);
  const inputRef = useRef(null);

  function addFiles(files) {
    const arr = Array.from(files).map((f) => ({
      file: f,
      id: crypto?.randomUUID?.() || Math.random().toString(36).slice(2),
      preview: isImage(f) ? URL.createObjectURL(f) : null,
      progress: 0,
      status: "pending",
      error: null,
    }));
    setItems((s) => [...arr, ...s]);
    for (const it of arr) uploadSingle(it);
  }

  function onDrop(e) {
    e.preventDefault();
    setIsDragging(false);
    addFiles(e.dataTransfer.files);
  }

  function onDragOver(e) {
    e.preventDefault();
    setIsDragging(true);
  }

  function onDragLeave(e) {
    e.preventDefault();
    setIsDragging(false);
  }

  async function uploadSingle(item) {
    const { file, id } = item;
    const fd = new FormData();
    fd.append("file", file, file.name);

    // Use XHR to report progress
    const xhr = new XMLHttpRequest();
    xhr.open("POST", joinApiRoute("/files"), true);
    if (UPLOAD_KEY) {
      try {
        xhr.setRequestHeader("X-API-KEY", UPLOAD_KEY);
      } catch (e) {
        // some environments may not allow setRequestHeader before send for CORS; ignore
      }
    }

    xhr.upload.onprogress = (ev) => {
      const pct = ev.lengthComputable ? Math.round((ev.loaded / ev.total) * 100) : 0;
      setItems((prev) => prev.map((p) => (p.id === id ? { ...p, progress: pct } : p)));
    };

    xhr.onload = () => {
      if (xhr.status >= 200 && xhr.status < 300) {
        setItems((prev) => prev.map((p) => (p.id === id ? { ...p, status: "done", progress: 100 } : p)));
        onUploaded?.();
      } else {
        let msg = `Upload failed (${xhr.status})`;
        try {
          const json = JSON.parse(xhr.responseText || "{}");
          msg = json.error || msg;
        } catch (e) {}
        setItems((prev) => prev.map((p) => (p.id === id ? { ...p, status: "error", error: msg } : p)));
      }
    };

    xhr.onerror = () => {
      setItems((prev) => prev.map((p) => (p.id === id ? { ...p, status: "error", error: "Network error" } : p)));
    };

    try {
      xhr.send(fd);
      setItems((prev) => prev.map((p) => (p.id === id ? { ...p, status: "uploading" } : p)));
    } catch (e) {
      setItems((prev) => prev.map((p) => (p.id === id ? { ...p, status: "error", error: e.message } : p)));
    }
  }

  return (
    <div>
      <div
        onDrop={onDrop}
        onDragOver={onDragOver}
        onDragLeave={onDragLeave}
        style={{
          border: isDragging ? "2px solid #3b82f6" : "2px dashed #cbd5e1",
          backgroundColor: isDragging ? "#eff6ff" : "transparent",
          padding: 16,
          borderRadius: 8,
          display: "flex",
          gap: 12,
          alignItems: "center",
          justifyContent: "space-between",
          marginBottom: 8,
          transition: "all 0.2s ease",
          transform: isDragging ? "scale(1.02)" : "scale(1)",
        }}
      >
        <div>
          <strong style={{ color: isDragging ? "#3b82f6" : "inherit" }}>
            {isDragging ? "📦 Drop files here!" : "Drag & drop files here"}
          </strong>
          <div style={{ fontSize: 12, color: "#475569" }}>Images, videos, PDFs, DOCX, text</div>
        </div>
        <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
          <input
            ref={inputRef}
            type="file"
            multiple
            onChange={(e) => addFiles(e.target.files)}
            style={{ display: "none" }}
          />
          <button
            onClick={() => inputRef.current && inputRef.current.click()}
            style={{ padding: "6px 10px" }}
          >
            Select files
          </button>
        </div>
      </div>

      {items.length > 0 && (
        <div style={{ display: "grid", gap: 8 }}>
          {items.map((it) => (
            <div key={it.id} style={{ display: "flex", gap: 12, alignItems: "center" }}>
              <div style={{ width: 56, height: 56, borderRadius: 6, overflow: "hidden", background: "#f8fafc", display: "flex", alignItems: "center", justifyContent: "center" }}>
                {it.preview ? (
                  <img src={it.preview} alt="preview" style={{ width: "100%", height: "100%", objectFit: "cover" }} />
                ) : (
                  <div style={{ fontSize: 12, color: "#475569", padding: 6 }}>{it.file.name.split(".").pop()}</div>
                )}
              </div>
              <div style={{ flex: 1 }}>
                <div style={{ fontSize: 13, fontWeight: 600 }}>{it.file.name}</div>
                <div style={{ fontSize: 12, color: "#64748b", marginTop: 4 }}>
                  {it.status === "uploading" ? `Uploading — ${it.progress}%` : it.status}
                  {it.error && <span style={{ color: "#dc2626", marginLeft: 8 }}>{it.error}</span>}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
