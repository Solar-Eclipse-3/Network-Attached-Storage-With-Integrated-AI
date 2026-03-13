import React, { useState, useEffect } from "react";
import UploadManager from "./UploadManager";

const API_BASE = import.meta.env.VITE_API_BASE ?? "/api";
const joinApiRoute = (path = "") => {
  const normalizedPath = path.startsWith("/") ? path : `/${path}`;
  const base = API_BASE.endsWith("/") ? API_BASE.slice(0, -1) : API_BASE;
  return `${base}${normalizedPath}`;
};
const parseJsonSafe = async (res, fallback = {}) => {
  const text = await res.text();
  if (!text) return fallback;
  try {
    return JSON.parse(text);
  } catch (err) {
    console.error("Failed to parse JSON", err);
    throw new Error("Invalid response from backend.");
  }
};

const normalizeFiles = (files = []) =>
  files.map((file) => {
    const preferred = file.download_path || file.url || "";
    const url = preferred.startsWith("http")
      ? preferred
      : preferred
      ? joinApiRoute(preferred)
      : "";
    return { ...file, url };
  });

const TypingIndicator = () => (
  <div style={{ display: "flex", gap: 4, padding: "8px 12px", background: "#eee", borderRadius: 12, width: "fit-content" }}>
    <span style={{ animation: "bounce 1.4s infinite", animationDelay: "0s" }}>●</span>
    <span style={{ animation: "bounce 1.4s infinite", animationDelay: "0.2s" }}>●</span>
    <span style={{ animation: "bounce 1.4s infinite", animationDelay: "0.4s" }}>●</span>
    <style>{`
      @keyframes bounce {
        0%, 60%, 100% { transform: translateY(0); opacity: 0.4; }
        30% { transform: translateY(-8px); opacity: 1; }
      }
    `}</style>
  </div>
);

export default function Chatbot() {
  const [messages, setMessages] = useState([
    { from: "bot", text: "Hi! I'm your NAS assistant 🤖. Ask me anything!" },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [filesList, setFilesList] = useState([]);
  const [suggestedQuestions, setSuggestedQuestions] = useState([]);

  useEffect(() => {
    fetchFiles();
  }, []);

  useEffect(() => {
    // Generate suggested questions based on files
    if (filesList.length > 0) {
      const pdfCount = filesList.filter(f => f.type === 'pdf').length;
      const imageCount = filesList.filter(f => f.type === 'image').length;
      const questions = [];
      
      if (pdfCount > 0) {
        questions.push("What documents do I have?");
        questions.push("Summarize my PDF files");
      }
      if (imageCount > 0) {
        questions.push("Show me all my pictures");
        questions.push("Create an album of my photos");
      }
      if (filesList.length > 0) {
        questions.push("What files did I upload today?");
      }
      setSuggestedQuestions(questions.slice(0, 3));
    }
  }, [filesList]);

  async function fetchFiles() {
    try {
      const res = await fetch(joinApiRoute("/files"));
      const data = await parseJsonSafe(res, { files: [] });
      if (res.ok) {
        setFilesList(normalizeFiles(data.files || []));
      }
    } catch (e) {
      // ignore
    }
  }

  async function sendMessage(e) {
    e.preventDefault();
    if (!input.trim()) return;

    const userMsg = { from: "user", text: input };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);
    setError("");

      try {
      const res = await fetch(joinApiRoute("/chat"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: userMsg.text }),
      });

      const data = await parseJsonSafe(res);
      if (!res.ok) {
        throw new Error(data.error || "Chat request failed");
      }
      const botMsg = {
        from: "bot",
        text: data.answer,
        sources: data.sources || [],
        files: normalizeFiles(data.files || []),
        album: data.album || null,
        suggestion: data.suggestion || null,
      };
      setMessages((prev) => [...prev, botMsg]);
    } catch (err) {
      console.error(err);
      setError("Chatbot backend not reachable. Make sure the Flask server is running (`python chatbot_server.py`).");
      setMessages((prev) => [
        ...prev,
        { from: "bot", text: "⚠️ Chatbot backend not reachable." },
      ]);
    }

    setLoading(false);
  }

  return (
    <div style={{ maxWidth: 600, margin: "0 auto", padding: 20 }}>
      <h2>FOCA 🦭</h2>

      <div
        style={{
          height: 400,
          overflowY: "auto",
          border: "1px solid #ccc",
          borderRadius: 8,
          padding: 10,
          marginBottom: 8,
        }}
      >
        {messages.map((msg, i) => (
          <div
            key={i}
            style={{
              textAlign: msg.from === "user" ? "right" : "left",
              margin: "6px 0",
            }}
          >
            <span
              style={{
                display: "inline-block",
                padding: "8px 12px",
                borderRadius: 12,
                background: msg.from === "user" ? "#cce4ff" : "#eee",
                whiteSpace: "pre-wrap",
              }}
            >
              {msg.text}
            </span>
            {msg.album && (
              <div
                style={{
                  marginTop: 6,
                  fontSize: "0.85rem",
                  color: "#3b82f6",
                }}
              >
                Album: {msg.album.name} ({msg.album.file_ids.length} files)
              </div>
            )}
            {msg.suggestion && (
              <div style={{ marginTop: 8, display: "flex", gap: 8, alignItems: "center" }}>
                <div style={{ fontSize: "0.9rem" }}>
                  Create album "{msg.suggestion.name}" with {msg.suggestion.file_ids.length} files?
                </div>
                <button
                    onClick={async () => {
                    try {
                      const headers = { "Content-Type": "application/json" };
                      const UPLOAD_KEY = import.meta.env.VITE_UPLOAD_KEY;
                      if (UPLOAD_KEY) headers["X-API-KEY"] = UPLOAD_KEY;
                      const res = await fetch(joinApiRoute("/albums"), {
                        method: "POST",
                        headers,
                        body: JSON.stringify({ name: msg.suggestion.name, file_ids: msg.suggestion.file_ids }),
                      });
                      const data = await res.json();
                      if (!res.ok) throw new Error(data.error || "Create album failed");
                      // Append a bot message confirming creation
                      setMessages((prev) => [
                        ...prev,
                        { from: "bot", text: `Created album '${data.album.name}' with ${data.album.file_ids.length} files.`, album: data.album },
                      ]);
                    } catch (e) {
                      setMessages((prev) => [...prev, { from: "bot", text: `Failed to create album: ${e.message}` }]);
                    }
                  }}
                  style={{ padding: "6px 10px" }}
                >
                  Create album
                </button>
              </div>
            )}
            {msg.files?.length > 0 && (
              <div
                style={{
                  marginTop: 8,
                  display: "flex",
                  flexWrap: "wrap",
                  gap: 8,
                }}
              >
                {msg.files.map((file) => {
                  const icon = file.type === 'pdf' ? '📄' : file.type === 'image' ? '🖼️' : file.type === 'video' ? '🎥' : '📎';
                  return (
                    <a
                      key={file.id || file.url}
                      href={file.url}
                      target="_blank"
                      rel="noreferrer"
                      style={{
                        border: "1px solid #cbd5e1",
                        borderRadius: 8,
                        padding: "8px 12px",
                        fontSize: "0.85rem",
                        textDecoration: "none",
                        color: "#0f172a",
                        background: "#ffffff",
                        display: "flex",
                        alignItems: "center",
                        gap: 6,
                        transition: "all 0.2s",
                        boxShadow: "0 1px 2px rgba(0,0,0,0.05)",
                      }}
                      onMouseOver={(e) => {
                        e.currentTarget.style.borderColor = "#3b82f6";
                        e.currentTarget.style.boxShadow = "0 2px 4px rgba(59,130,246,0.2)";
                      }}
                      onMouseOut={(e) => {
                        e.currentTarget.style.borderColor = "#cbd5e1";
                        e.currentTarget.style.boxShadow = "0 1px 2px rgba(0,0,0,0.05)";
                      }}
                    >
                      <span>{icon}</span>
                      <span style={{ fontWeight: 500 }}>{file.name}</span>
                      <span style={{ color: "#94a3b8", fontSize: "0.75rem" }}>({file.type})</span>
                    </a>
                  );
                })}
              </div>
            )}
            {msg.sources?.length > 0 && (
              <div style={{ marginTop: 6, fontSize: "0.75rem", color: "#475569" }}>
                Sources:{" "}
                {msg.sources.map((source) => source.path).join(", ")}
              </div>
            )}
          </div>
        ))}
        {loading && <TypingIndicator />}
      </div>
      <UploadManager onUploaded={fetchFiles} />

      {suggestedQuestions.length > 0 && messages.length <= 3 && (
        <div style={{ marginBottom: 12, marginTop: 12 }}>
          <div style={{ fontSize: "0.85rem", color: "#64748b", marginBottom: 6 }}>Try asking:</div>
          <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
            {suggestedQuestions.map((q, idx) => (
              <button
                key={idx}
                onClick={() => setInput(q)}
                style={{
                  fontSize: "0.8rem",
                  padding: "6px 12px",
                  border: "1px solid #e2e8f0",
                  borderRadius: 16,
                  background: "#f8fafc",
                  cursor: "pointer",
                  color: "#475569",
                }}
              >
                💡 {q}
              </button>
            ))}
          </div>
        </div>
      )}

      {filesList.length > 0 && (
        <div style={{ marginBottom: 12 }}>
          <strong>Files:</strong>
          <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginTop: 6 }}>
            {filesList.map((f) => (
              <a key={f.id} href={f.url} target="_blank" rel="noreferrer" style={{ fontSize: 12, padding: "4px 8px", border: "1px solid #e2e8f0", borderRadius: 6, background: "#fbfcfe" }}>
                {f.name}
              </a>
            ))}
          </div>
        </div>
      )}
      {error && (
        <div style={{ color: "#dc2626", marginBottom: 8, fontSize: "0.9rem" }}>
          {error}
        </div>
      )}

      <form onSubmit={sendMessage} style={{ display: "flex", gap: 8 }}>
        <input
          style={{ flex: 1, padding: 8 }}
          placeholder="Ask something about your NAS..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={loading}
        />
        <button style={{ padding: "0 18px" }} disabled={loading}>
          Send
        </button>
      </form>
    </div>
  );
}
