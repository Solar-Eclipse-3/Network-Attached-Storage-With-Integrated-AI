import Chatbot from "./Chatbot";
import { useState, useEffect, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  FaFileAlt,
  FaFileImage,
  FaFileVideo,
  FaFilePdf,
  FaDownload,
  FaBars,
  FaMoon,
  FaSun,
} from "react-icons/fa";
import { IoCloseSharp } from "react-icons/io5";
import Signup from "./Signup";
import Login from "./Login";
import ImageGallery from "./ImageGallery";

// const API_BASE = import.meta.env.VITE_API_BASE ?? "/api";
const API_BASE = import.meta.env.VITE_API_BASE ?? "http://127.0.0.1:5001";
const UPLOAD_KEY = import.meta.env.VITE_UPLOAD_KEY ?? null;
const apiRoute = (path = "") => {
  const normalizedPath = path.startsWith("/") ? path : `/${path}`;
  const base = API_BASE.endsWith("/")
    ? API_BASE.slice(0, -1)
    : API_BASE;
  return `${base}${normalizedPath}`;
};

const MotionDiv = motion.div;
const parseJsonSafe = async (res, fallback = {}) => {
  const text = await res.text();
  if (!text) return fallback;
  try {
    return JSON.parse(text);
  } catch (err) {
    console.error("Failed to parse JSON", err);
    throw new Error("Server returned an unexpected response.");
  }
};

const withClientPaths = (file) => {
  if (!file) return file;
  const preferred = file.download_path || file.url || file.src || "";
  const absolutePath = preferred.startsWith("http")
    ? preferred
    : preferred
    ? apiRoute(preferred)
    : "";
  return { ...file, url: absolutePath, src: absolutePath };
};

function App() {
  const [showSignup, setShowSignup] = useState(true);
  const [userEmail, setUserEmail] = useState(null);
  const [selectedCategory, setSelectedCategory] = useState("All Files");
  const [searchQuery, setSearchQuery] = useState("");
  const [previewFile, setPreviewFile] = useState(null);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [loginSuccess, setLoginSuccess] = useState(false);

  // 🌙 Dark mode
  const [darkMode, setDarkMode] = useState(false);

  // ✅ Load saved theme from localStorage when app starts
useEffect(() => {
  const savedTheme = localStorage.getItem("darkMode");
  if (savedTheme !== null) {
    setDarkMode(savedTheme === "true");
    console.log("🌙 Loaded theme:", savedTheme);
  }
}, []);


  // Centralized theme tokens (only for colors)
  const theme = darkMode
    ? {
        bg: "#0b0c10",
        text: "#66fcf1",
        primary: "#66fcf1",
        primaryContr: "#0b0c10",
        cardBg: "#1f2833",
        panelBg: "#14181f",
        border: "#2b3645",
        mutedText: "#94a3b8",
        light: "#e2e8f0",
        danger: "#E52424",
        overlay: "rgba(0,0,0,0.85)",
        chipBg: "#0f172a",
      }
    : {
        bg: "white",
        text: "#007BFF",
        primary: "#007BFF",
        primaryContr: "white",
        cardBg: "#f8f9fa",
        panelBg: "white",
        border: "#e2e8f0",
        mutedText: "#94a3b8",
        light: "#ffffff",
        danger: "#E52424",
        overlay: "rgba(0,0,0,0.85)",
    chipBg: "#fff",
    };

// File list and upload state
const [files, setFiles] = useState([]);
const [filesLoading, setFilesLoading] = useState(true);
const [uploading, setUploading] = useState(false);
const [uploadError, setUploadError] = useState("");
const [storageUsed, setStorageUsed] = useState(0);
const [fileStats, setFileStats] = useState({ documents: 0, images: 0, videos: 0, total: 0 });
const [selectedFiles, setSelectedFiles] = useState([]);
const [bulkMode, setBulkMode] = useState(false);

// 🔹 NEW: Delete confirmation modal state
const [confirmOpen, setConfirmOpen] = useState(false);
const [pendingDelete, setPendingDelete] = useState(null);

// 📁 Albums state
const [albums, setAlbums] = useState([]);
const [selectedAlbum, setSelectedAlbum] = useState(null);

const handleLogout = () => setUserEmail(null);
const categories = ["All Files", "Documents", "Pictures", "Videos", "Albums"];

const formatBytes = (bytes) => {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
};

const toggleFileSelection = (fileId) => {
  setSelectedFiles(prev => 
    prev.includes(fileId) ? prev.filter(id => id !== fileId) : [...prev, fileId]
  );
};

const selectAllFiles = () => {
  if (selectedFiles.length === filteredFiles.length) {
    setSelectedFiles([]);
  } else {
    setSelectedFiles(filteredFiles.map(f => f.id));
  }
};

const bulkDelete = async () => {
  if (!selectedFiles.length) return;
  try {
    await Promise.all(selectedFiles.map(id => 
      fetch(apiRoute(`/files/${id}`), { method: "DELETE" })
    ));
    setFiles(prev => prev.filter(f => !selectedFiles.includes(f.id)));
    setSelectedFiles([]);
    setBulkMode(false);
  } catch (err) {
    console.error("Bulk delete failed", err);
    setUploadError("Failed to delete some files.");
  }
};

const bulkDownload = async () => {
  if (!selectedFiles.length) return;
  // Create a simple HTML page that triggers downloads
  const selectedFileObjects = files.filter(f => selectedFiles.includes(f.id));
  for (const file of selectedFileObjects) {
    const a = document.createElement('a');
    a.href = file.url;
    a.download = file.name || 'download';
    a.click();
    await new Promise(resolve => setTimeout(resolve, 200)); // Small delay between downloads
  }
};

const fetchFiles = useCallback(async () => {
  try {
    setFilesLoading(true);
    const res = await fetch(apiRoute("/files"));
    const data = await parseJsonSafe(res, { files: [] });
    if (!res.ok) throw new Error(data.error || "Failed to fetch files");
    const normalized = (data.files || []).map(withClientPaths);
    setFiles(normalized);
  } catch (err) {
    console.error("Failed to fetch files", err);
  } finally {
    setFilesLoading(false);
  }
}, []);

useEffect(() => {
  fetchFiles();
}, [fetchFiles]);

// Fetch albums
const fetchAlbums = useCallback(async () => {
  try {
    const res = await fetch(apiRoute("/albums"));
    const data = await parseJsonSafe(res, { albums: [] });
    if (!res.ok) throw new Error(data.error || "Failed to fetch albums");
    setAlbums(data.albums || []);
  } catch (err) {
    console.error("Failed to fetch albums", err);
  }
}, []);

useEffect(() => {
  fetchAlbums();
}, [fetchAlbums]);

// Calculate storage usage and file statistics
useEffect(() => {
  const totalBytes = files.reduce((sum, f) => sum + (f.size || 0), 0);
  setStorageUsed(totalBytes);
  
  const stats = files.reduce(
    (acc, f) => {
      acc.total++;
      if (['txt', 'pdf', 'doc', 'docx'].includes(f.type)) acc.documents++;
      else if (f.type === 'image') acc.images++;
      else if (f.type === 'video') acc.videos++;
      return acc;
    },
    { documents: 0, images: 0, videos: 0, total: 0 }
  );
  setFileStats(stats);
}, [files]);

const handleFileUpload = async (event) => {
  const selected = Array.from(event.target?.files || []);
  if (!selected.length) return;

  setUploadError("");
  setUploading(true);

  try {
    for (const file of selected) {
      const formData = new FormData();
      formData.append("file", file, file.name);

      const res = await fetch(apiRoute("/files"), {
        method: "POST",
        headers: UPLOAD_KEY ? { "X-API-KEY": UPLOAD_KEY } : undefined,
        body: formData,
      });

      const data = await parseJsonSafe(res);
      if (!res.ok) {
        throw new Error(data.error || "Upload failed");
      }

      if (data.file) {
        // const normalized = withClientPaths(data.file);
                const baseName = file.name.toLowerCase();
        let tags = [file.type]; // always include type

        if (baseName.includes("car1")) tags.push("car", "blue");
        if (baseName.includes("car2")) tags.push("car", "red");
        if (baseName.includes("car3")) tags.push("car", "white");
        if (baseName.includes("logo")) tags.push("logo");

        const normalized = { ...withClientPaths(data.file), tags };
        setFiles((prev) => [normalized, ...prev]);
      }
    }
  } catch (err) {
    console.error("Upload failed", err);
    const message =
      err.message === "Failed to fetch"
        ? "Upload failed: backend not reachable. Is the Flask server running on port 5001?"
        : err.message || "Failed to upload file.";
    setUploadError(message);
  } finally {
    setUploading(false);
    if (event.target) event.target.value = "";
    fetchFiles();
  }
};

const handleDeleteFile = async (fileId) => {
    try {
      const res = await fetch(apiRoute(`/files/${fileId}`), {
        method: "DELETE",
      });
      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.error || "Failed to delete file");
      }
      setFiles((prev) => prev.filter((f) => f.id !== fileId));
    } catch (err) {
      console.error("Delete failed", err);
      setUploadError(err.message || "Failed to delete file.");
    }
  };

  // 🔹 NEW: open/close/confirm helpers for modal
  const askDelete = (file) => {
    setPendingDelete(file);
    setConfirmOpen(true);
  };

  const cancelDelete = () => {
    setConfirmOpen(false);
    setPendingDelete(null);
  };

  const confirmDelete = async () => {
    if (pendingDelete) {
      await handleDeleteFile(pendingDelete.id);
    }
    setConfirmOpen(false);
    setPendingDelete(null);
  };

  // (Optional) Esc to close modal
  useEffect(() => {
    const onKey = (e) => {
      if (e.key === "Escape") setConfirmOpen(false);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  const getFileIcon = (type) => {
    const size = 22;
    const color = theme.primary;
    switch (type) {
      case "pdf":
        return <FaFilePdf size={size} color={color} />;
      case "image":
        return <FaFileImage size={size} color={color} />;
      case "video":
        return <FaFileVideo size={size} color={color} />;
      default:
        return <FaFileAlt size={size} color={color} />;
    }
  };

  const filteredFiles = files.filter((file, index, self) => {
    const isUnique = file.id
      ? index === self.findIndex((f) => f.id === file.id)
      : index === self.findIndex((f) => f.src === file.src);

    let matchCategory = false;
    switch (selectedCategory) {
      case "All Files":
        matchCategory = true;
        break;
      case "Documents":
        matchCategory =
          ["txt", "pdf", "doc", "docx", "other"].includes(file.type);
        break;
      case "Pictures":
        matchCategory = file.type === "image";
        break;
      case "Videos":
        matchCategory = file.type === "video";
        break;
      default:
        matchCategory = true;
    }

    // const matchSearch = file.name
    //   ?.toLowerCase()
    //   .includes(searchQuery.toLowerCase());
    
      const matchSearch = 
      file.name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      file.tags?.some((tag) => tag.toLowerCase().includes(searchQuery.toLowerCase()));

    return isUnique && matchCategory && matchSearch;
  });

  useEffect(() => {
    if (userEmail) {
      setLoginSuccess(true);
      setTimeout(() => setLoginSuccess(false), 2000);
    }
  }, [userEmail]);

  // ✅ Save theme changes to localStorage whenever darkMode updates
  useEffect(() => {
    localStorage.setItem("darkMode", darkMode);
    console.log("💾 Saved theme:", darkMode);
  }, [darkMode]);

  const openPreview = async (file) => {
    if (file.type === "txt") {
      try {
        const res = await fetch(file.url);
        const text = await res.text();
        setPreviewFile({ ...file, content: text });
      } catch (err) {
        console.error("Failed to preview file", err);
        setPreviewFile({
          ...file,
          content: "Unable to load preview for this file.",
        });
      }
      return;
    }
    setPreviewFile(file);
  };

  return (
    <div
      style={{
        height: "100vh",
        width: "100vw",
        fontFamily: "Arial, sans-serif",
        backgroundColor: theme.bg,
        color: theme.text,
        overflow: "hidden",
        position: "relative",
        transition: "background-color 0.3s ease, color 0.3s ease",
      }}
    >
      {/* Sidebar Button */}
      {userEmail && (
        <div
          style={{
            position: "fixed",
            top: "20px",
            left: "20px",
            zIndex: 20,
          }}
        >
          <button
            onClick={() => setSidebarOpen(true)}
            style={{
              width: "45px",
              height: "45px",
              border: "none",
              backgroundColor: theme.panelBg,
              borderRadius: "8px",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              cursor: "pointer",
              boxShadow: "0 2px 6px rgba(0,0,0,0.15)",
            }}
          >
            <FaBars size={22} color={theme.primary} />
          </button>
        </div>
      )}

      {/* 🌙 Dark Mode Toggle Button */}
      <div
        style={{
          position: "fixed",
          top: "20px",
          right: "20px",
          zIndex: 20,
        }}
      >
        <button
          onClick={() => setDarkMode((prev) => !prev)}
          style={{
            width: "45px",
            height: "45px",
            border: "none",
            borderRadius: "8px",
            backgroundColor: theme.panelBg,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            cursor: "pointer",
            boxShadow: "0 2px 6px rgba(0,0,0,0.15)",
            transition: "0.3s",
          }}
          title={darkMode ? "Switch to light mode" : "Switch to dark mode"}
        >
          {darkMode ? (
            <FaSun size={22} color="#f1c40f" />
          ) : (
            <FaMoon size={22} color={theme.primary} />
          )}
        </button>
      </div>

      {/* ✅ LOGO + TITLE */}
      <div
        style={{
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          marginTop: "30px",
        }}
      >
        <img
          src="/images/Logo.png"
          alt="Smart NAS Logo"
          style={{
            height: 48,
            width: 48,
            marginRight: 10,
            objectFit: "contain",
            filter: darkMode ? "brightness(0.85)" : "none",
          }}
          onError={(e) => (e.target.style.display = "none")}
        />
        <h1
          style={{
            fontSize: "2.8rem",
            fontWeight: "bold",
            color: theme.primary,
            margin: 0,
          }}
        >
          SMART NAS
        </h1>
      </div>

      {/* ✅ Login Successful Toast */}
      <AnimatePresence>
        {loginSuccess && (
          <MotionDiv
            initial={{ opacity: 0, x: 50 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 50 }}
            transition={{ duration: 0.4 }}
            style={{
              position: "fixed",
              top: "20px",
              right: "20px",
              backgroundColor: theme.panelBg,
              color: theme.primary,
              border: `2px solid ${theme.primary}`,
              borderRadius: "10px",
              padding: "10px 18px",
              boxShadow: "0 4px 10px rgba(0,0,0,0.1)",
              fontWeight: "bold",
              display: "flex",
              alignItems: "center",
              gap: "8px",
              zIndex: 999,
            }}
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="18"
              height="18"
              fill={theme.primary}
              viewBox="0 0 16 16"
            >
              <path d="M13.485 1.929a.75.75 0 0 1 0 1.06L6.75 9.724 2.515 5.49a.75.75 0 1 1 1.06-1.06l3.175 3.174 6.27-6.27a.75.75 0 0 1 1.06 0z" />
            </svg>
            Login Successful
          </MotionDiv>
        )}
      </AnimatePresence>

      {/* Login or File Manager */}
      {!userEmail ? (
        <div
          style={{
            flex: 1,
            display: "flex",
            flexDirection: "column",
            justifyContent: "center",
            alignItems: "center",
            height: "100%",
          }}
        >
          {showSignup ? (
            <Signup setUserEmail={setUserEmail} />
          ) : (
            <Login setUserEmail={setUserEmail} />
          )}
          <button
            onClick={() => setShowSignup(!showSignup)}
            style={{
              marginTop: "25px",
              padding: "10px 22px",
              backgroundColor: theme.primary,
              color: theme.primaryContr,
              border: "none",
              borderRadius: "20px",
              cursor: "pointer",
              fontWeight: "bold",
            }}
          >
            {showSignup
              ? "Already have an account? Login"
              : "Need an account? Sign Up"}
          </button>
        </div>
      ) : (
        <MotionDiv
          animate={{ x: sidebarOpen ? 250 : 0 }}
          transition={{ duration: 0.4, ease: "easeInOut" }}
          style={{
            flex: 1,
            display: "flex",
            height: "calc(100vh - 80px)",
            marginTop: "20px",
            overflow: "hidden",
          }}
        >
          {/* File Grid */}
          <div
            style={{
              flex: 1,
              padding: "20px",
              display: "flex",
              flexDirection: "column",
              gap: "20px",
              overflowY: "auto",
            }}
          >
            {/* <ImageGallery
              useSearchResults={true}
              files={files.filter((file) => file.type === "image")}
            /> */}

            <input
              type="text"
              placeholder="Search files..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              style={{
                padding: "10px",
                borderRadius: "15px",
                border: `1px solid ${theme.primary}`,
                fontSize: "1rem",
                backgroundColor: darkMode ? "#0f172a" : "#f8f9fa",
                color: theme.primary,
              }}
            />
            
            {/* 📊 Storage Usage Indicator */}
            {files.length > 0 && (
              <div style={{
                backgroundColor: theme.cardBg,
                padding: "16px",
                borderRadius: "12px",
                border: `1px solid ${theme.border}`,
              }}>
                <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "8px" }}>
                  <span style={{ fontSize: "0.9rem", fontWeight: 600 }}>Storage Used</span>
                  <span style={{ fontSize: "0.9rem", color: theme.mutedText }}>{formatBytes(storageUsed)} / 100 GB</span>
                </div>
                <div style={{
                  width: "100%",
                  height: "8px",
                  backgroundColor: darkMode ? "#1f2937" : "#e2e8f0",
                  borderRadius: "4px",
                  overflow: "hidden",
                }}>
                  <div style={{
                    width: `${Math.min((storageUsed / (100 * 1024 * 1024 * 1024)) * 100, 100)}%`,
                    height: "100%",
                    backgroundColor: theme.primary,
                    transition: "width 0.3s ease",
                  }} />
                </div>
                <div style={{
                  display: "flex",
                  gap: "16px",
                  marginTop: "12px",
                  fontSize: "0.85rem",
                  color: theme.mutedText,
                }}>
                  <span>📄 {fileStats.documents} docs</span>
                  <span>🖼️ {fileStats.images} images</span>
                  <span>🎥 {fileStats.videos} videos</span>
                  <span>📁 {fileStats.total} total</span>
                </div>
              </div>
            )}
            
            {/* Chatbot inserted here — appears under search and upload controls */}
            <div style={{ marginTop: 16 }}>
              <Chatbot />
            </div>
            
            {/* Bulk Operations Toolbar */}
            {files.length > 0 && (
              <div style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                padding: "12px 16px",
                backgroundColor: theme.cardBg,
                borderRadius: "8px",
                border: `1px solid ${theme.border}`,
                marginBottom: "12px",
              }}>
                <div style={{ display: "flex", gap: 12, alignItems: "center" }}>
                  <button
                    onClick={() => {
                      setBulkMode(!bulkMode);
                      setSelectedFiles([]);
                    }}
                    style={{
                      padding: "6px 12px",
                      borderRadius: "6px",
                      border: `1px solid ${theme.primary}`,
                      background: bulkMode ? theme.primary : "transparent",
                      color: bulkMode ? theme.primaryContr : theme.primary,
                      cursor: "pointer",
                      fontSize: "0.85rem",
                      fontWeight: 600,
                    }}
                  >
                    {bulkMode ? "✓ Select Mode" : "Select Multiple"}
                  </button>
                  {bulkMode && filteredFiles.length > 0 && (
                    <button
                      onClick={selectAllFiles}
                      style={{
                        padding: "6px 12px",
                        borderRadius: "6px",
                        border: `1px solid ${theme.border}`,
                        background: "transparent",
                        color: theme.text,
                        cursor: "pointer",
                        fontSize: "0.85rem",
                      }}
                    >
                      {selectedFiles.length === filteredFiles.length ? "Deselect All" : "Select All"}
                    </button>
                  )}
                  {selectedFiles.length > 0 && (
                    <span style={{ fontSize: "0.85rem", color: theme.mutedText }}>
                      {selectedFiles.length} selected
                    </span>
                  )}
                </div>
                <div style={{ display: "flex", gap: 8 }}>
                  {selectedFiles.length >= 0 && (
                    <>
                      <button
                        onClick={bulkDownload}
                        style={{
                          padding: "6px 12px",
                          borderRadius: "6px",
                          border: `1px solid ${theme.primary}`,
                          background: theme.primary,
                          color: theme.primaryContr,
                          cursor: "pointer",
                          fontSize: "0.85rem",
                          fontWeight: 600,
                          display: "flex",
                          alignItems: "center",
                          gap: 6,
                        }}
                      >
                        <FaDownload size={12} /> Download ({selectedFiles.length})
                      </button>
                      <button
                        onClick={bulkDelete}
                        style={{
                          padding: "6px 12px",
                          borderRadius: "6px",
                          border: `1px solid ${theme.danger}`,
                          background: theme.danger,
                          color: "white",
                          cursor: "pointer",
                          fontSize: "0.85rem",
                          fontWeight: 600,
                        }}
                      >
                        Delete ({selectedFiles.length})
                      </button>
                    </>
                  )}
                  <label
                    style={{
                      backgroundColor: theme.primary,
                      color: theme.primaryContr,
                      padding: "6px 12px",
                      borderRadius: "6px",
                      cursor: "pointer",
                      fontWeight: 600,
                      fontSize: "0.85rem",
                    }}
                  >
                    {uploading ? "Uploading..." : "+ Upload"}
                    <input
                      type="file"
                      accept="*"
                      multiple
                      onChange={handleFileUpload}
                      disabled={uploading}
                      style={{ display: "none" }}
                    />
                  </label>
                </div>
              </div>
            )}
            
            <div style={{ display: "flex", justifyContent: "flex-end" }}>
            </div>
            {uploadError && (
              <div style={{ color: theme.danger, fontSize: "0.9rem" }}>
                {uploadError}
              </div>
            )}
            
            {/* Albums View */}
            {selectedCategory === "Albums" ? (
              <div>
                <h2 style={{ color: theme.primary, marginBottom: "16px" }}>📁 Your Albums</h2>
                {albums.length === 0 ? (
                  <div style={{ color: theme.mutedText, fontStyle: "italic" }}>
                    No albums yet. Ask the chatbot to create one! (e.g., "Create an album of my car pictures")
                  </div>
                ) : (
                  <div
                    style={{
                      display: "grid",
                      gridTemplateColumns: "repeat(auto-fill, minmax(200px, 1fr))",
                      gap: "20px",
                    }}
                  >
                    {albums.map((album) => {
                      const albumFiles = files.filter(f => album.file_ids.includes(f.id));
                      const thumbnail = albumFiles.find(f => f.type === "image");
                      
                      return (
                        <div
                          key={album.id}
                          onClick={() => setSelectedAlbum(album)}
                          style={{
                            backgroundColor: theme.cardBg,
                            borderRadius: "12px",
                            padding: "16px",
                            cursor: "pointer",
                            boxShadow: "0 3px 8px rgba(0,0,0,0.1)",
                            transition: "0.3s",
                          }}
                          onMouseOver={(e) => e.currentTarget.style.transform = "scale(1.05)"}
                          onMouseOut={(e) => e.currentTarget.style.transform = "scale(1.0)"}
                        >
                          {/* Thumbnail */}
                          <div
                            style={{
                              width: "100%",
                              height: "140px",
                              borderRadius: "8px",
                              backgroundColor: theme.panelBg,
                              marginBottom: "12px",
                              display: "flex",
                              alignItems: "center",
                              justifyContent: "center",
                              overflow: "hidden",
                            }}
                          >
                            {thumbnail ? (
                              <img
                                src={thumbnail.url}
                                alt={album.name}
                                style={{
                                  width: "100%",
                                  height: "100%",
                                  objectFit: "cover",
                                }}
                              />
                            ) : (
                              <span style={{ fontSize: "48px" }}>📁</span>
                            )}
                          </div>
                          
                          {/* Album Name */}
                          <div style={{ 
                            color: theme.primary, 
                            fontWeight: "700", 
                            fontSize: "1.1rem",
                            marginBottom: "6px",
                          }}>
                            {album.name}
                          </div>
                          
                          {/* File Count */}
                          <div style={{ 
                            color: theme.mutedText, 
                            fontSize: "0.85rem",
                          }}>
                            {album.file_ids.length} {album.file_ids.length === 1 ? 'file' : 'files'}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            ) : (
              /* Files Grid */
              <div
                style={{
                  display: "grid",
                  gridTemplateColumns: "repeat(auto-fill, minmax(150px, 1fr))",
                  gap: "20px",
                }}
              >
                {filesLoading ? (
                  <div style={{ color: theme.mutedText }}>Loading files...</div>
                ) : filteredFiles.length === 0 ? (
                  <div style={{ color: theme.mutedText, fontStyle: "italic" }}>
                    No files uploaded yet. Click "Upload File" to add one.
                  </div>
                ) : (
                  filteredFiles.map((file) => (
                  <div
                    key={file.id || file.src}
                    style={{
                      backgroundColor: theme.cardBg,
                      color: theme.primary,
                      padding: "10px",
                      borderRadius: "15px",
                      textAlign: "center",
                      fontWeight: "500",
                      cursor: "pointer",
                      boxShadow: selectedFiles.includes(file.id) 
                        ? `0 0 0 3px ${theme.primary}` 
                        : "0 3px 8px rgba(0,0,0,0.1)",
                      transition: "0.3s",
                      position: "relative",
                      opacity: bulkMode && !selectedFiles.includes(file.id) ? 0.6 : 1,
                    }}
                    onMouseOver={(e) =>
                      (e.currentTarget.style.transform = "scale(1.05)")
                    }
                    onMouseOut={(e) =>
                      (e.currentTarget.style.transform = "scale(1.0)")
                    }
                    onClick={(e) => {
                      if (bulkMode) {
                        e.stopPropagation();
                        toggleFileSelection(file.id);
                      } else {
                        openPreview(file);
                      }
                    }}
                  >
                    {/* Checkbox for bulk selection */}
                    {bulkMode && (
                      <div
                        style={{
                          position: "absolute",
                          top: "8px",
                          left: "8px",
                          width: "20px",
                          height: "20px",
                          borderRadius: "4px",
                          border: `2px solid ${theme.primary}`,
                          backgroundColor: selectedFiles.includes(file.id) ? theme.primary : "transparent",
                          display: "flex",
                          alignItems: "center",
                          justifyContent: "center",
                          color: theme.primaryContr,
                          fontSize: "12px",
                          fontWeight: "bold",
                        }}
                        onClick={(e) => {
                          e.stopPropagation();
                          toggleFileSelection(file.id);
                        }}
                      >
                        {selectedFiles.includes(file.id) && "✓"}
                      </div>
                    )}
                    
                    {/* 🔹 Top-right delete X — now opens modal */}
                    {!bulkMode && (
                      <button
                        aria-label="Delete file"
                        title="Delete file"
                        onClick={(e) => {
                          e.stopPropagation();
                          askDelete(file);
                        }}
                        style={{
                          position: "absolute",
                          top: "6px",
                          right: "6px",
                          background: "transparent",
                          border: "none",
                          color: theme.danger,
                          fontSize: "20px",
                          fontWeight: 800,
                          lineHeight: 1,
                          padding: 0,
                          cursor: "pointer",
                        }}
                        onMouseEnter={(e) =>
                          (e.currentTarget.style.transform = "scale(1.15)")
                        }
                        onMouseLeave={(e) =>
                          (e.currentTarget.style.transform = "scale(1)")
                        }
                      >
                        ×
                      </button>
                    )}

                    <div style={{ marginBottom: "8px" }}>
                      {getFileIcon(file.type)}
                    </div>
                    {file.type === "image" && (
                      <img
                        src={file.url}
                        alt={file.name}
                        style={{
                          width: "100%",
                          height: "80px",
                          objectFit: "cover",
                          borderRadius: "8px",
                          marginBottom: "5px",
                          filter: darkMode ? "brightness(0.95)" : "none",
                        }}
                      />
                    )}
                    {file.type === "video" && (
                      <video
                        src={file.url}
                        style={{
                          maxHeight: "80px",
                          borderRadius: "8px",
                          marginBottom: "5px",
                        }}
                        muted
                        loop
                      />
                    )}
                    {file.type === "pdf" && (
                      <div
                        style={{
                          height: "80px",
                          borderRadius: "8px",
                          backgroundColor: theme.light,
                          border: `1px solid ${theme.primary}`,
                          display: "flex",
                          alignItems: "center",
                          justifyContent: "center",
                          fontSize: "0.9rem",
                          marginBottom: "5px",
                        }}
                      >
                        PDF
                      </div>
                    )}
                    {file.type === "txt" && (
                      <div
                        style={{
                          height: "80px",
                          borderRadius: "8px",
                          backgroundColor: theme.light,
                          border: `1px solid ${theme.primary}`,
                          display: "flex",
                          alignItems: "center",
                          justifyContent: "center",
                          fontSize: "0.9rem",
                          marginBottom: "5px",
                        }}
                      >
                        Text
                      </div>
                    )}
                    <div>{file.name}</div>
                    {/* 🔹 don’t open preview */}
                    <a
                      href={file.url}
                      download
                      onClick={(e) => e.stopPropagation()}
                      style={{
                        marginTop: "8px",
                        display: "inline-block",
                        padding: "5px 8px",
                        backgroundColor: theme.primary,
                        color: theme.primaryContr,
                        borderRadius: "8px",
                        textDecoration: "none",
                        fontSize: "0.8rem",
                      }}
                    >
                      <FaDownload style={{ marginRight: "5px" }} />
                      Download
                    </a>
                  </div>
                ))
              )}
            </div>
            )}
          </div>
        </MotionDiv>
      )}

      {/* Sidebar */}
      <AnimatePresence>
        {sidebarOpen && (
          <MotionDiv
            initial={{ x: "-100%" }}
            animate={{ x: 0 }}
            exit={{ x: "-100%" }}
            transition={{ duration: 0.4 }}
            style={{
              position: "fixed",
              top: 0,
              left: 0,
              width: "250px",
              height: "100vh",
              backgroundColor: theme.panelBg,
              boxShadow: "3px 0 10px rgba(0,0,0,0.15)",
              display: "flex",
              flexDirection: "column",
              padding: "20px",
              zIndex: 100,
            }}
          >
            <div
              style={{
                display: "flex",
                justifyContent: "flex-end",
                marginBottom: "20px",
              }}
            >
              <IoCloseSharp
                size={30}
                color={theme.danger}
                style={{ cursor: "pointer" }}
                onClick={() => setSidebarOpen(false)}
              />
            </div>
            {categories.map((cat) => (
              <button
                key={cat}
                onClick={() => setSelectedCategory(cat)}
                style={{
                  padding: "12px",
                  marginBottom: "10px",
                  backgroundColor:
                    selectedCategory === cat ? theme.primary : theme.cardBg,
                  color:
                    selectedCategory === cat ? theme.primaryContr : theme.primary,
                  border: "none",
                  borderRadius: "10px",
                  cursor: "pointer",
                  textAlign: "left",
                  fontWeight: "500",
                  transition: "0.3s",
                }}
              >
                {cat}
              </button>
            ))}

            <button
              onClick={handleLogout}
              style={{
                position: "absolute",
                bottom: "60px",
                left: "20px",
                right: "20px",
                padding: "10px",
                backgroundColor: theme.cardBg,
                color: theme.danger,
                border: "none",
                borderRadius: "10px",
                cursor: "pointer",
                fontWeight: "500",
                boxShadow: "0 2px 6px rgba(0,0,0,0.1)",
              }}
            >
              Logout
            </button>
          </MotionDiv>
        )}
      </AnimatePresence>

      {/* Preview overlay */}
      {previewFile && (
        <div
          onClick={() => setPreviewFile(null)}
          style={{
            position: "fixed",
            top: 0,
            left: 0,
            width: "100vw",
            height: "100vh",
            backgroundColor: theme.overlay,
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            zIndex: 200,
            cursor: "pointer",
          }}
        >
          {previewFile.type === "image" ? (
            <img
              src={previewFile.src}
              alt={previewFile.name}
              style={{
                maxHeight: "90%",
                maxWidth: "90%",
                borderRadius: "15px",
              }}
            />
          ) : previewFile.type === "video" ? (
            <video
              src={previewFile.src}
              controls
              autoPlay
              style={{
                maxHeight: "90%",
                maxWidth: "90%",
                borderRadius: "15px",
              }}
            />
          ) : previewFile.type === "pdf" ? (
            <iframe
              src={previewFile.src}
              title={previewFile.name}
              style={{
                width: "80%",
                height: "80%",
                border: "none",
                backgroundColor: theme.light,
                borderRadius: "10px",
              }}
            />
          ) : previewFile.type === "txt" ? (
            <div
              style={{
                backgroundColor: theme.light,
                color: theme.primary,
                padding: "20px",
                width: "70%",
                height: "70%",
                overflowY: "auto",
                borderRadius: "10px",
                fontFamily: "monospace",
                fontSize: "1rem",
              }}
            >
              <pre>{previewFile.content}</pre>
            </div>
          ) : null}
        </div>
      )}

      {/* 🔹 In-app delete confirmation modal */}
      <AnimatePresence>
        {confirmOpen && (
          <MotionDiv
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
            onClick={cancelDelete}
            style={{
              position: "fixed",
              inset: 0,
              background: "rgba(0,0,0,0.45)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              zIndex: 1000,
              backdropFilter: "blur(1px)",
              cursor: "default",
            }}
          >
            <MotionDiv
              initial={{ y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              exit={{ y: 20, opacity: 0 }}
              transition={{ duration: 0.2 }}
              onClick={(e) => e.stopPropagation()}
              role="dialog"
              aria-modal="true"
              style={{
                width: "min(92vw, 420px)",
                background: theme.panelBg,
                borderRadius: "16px",
                boxShadow: "0 10px 30px rgba(0,0,0,0.15)",
                padding: "20px",
                border: `1px solid ${theme.border}`,
                color: theme.primary,
              }}
            >
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 12,
                  marginBottom: 10,
                }}
              >
                <div
                  aria-hidden
                  style={{
                    width: 34,
                    height: 34,
                    borderRadius: 8,
                    background: darkMode
                      ? "rgba(229,36,36,0.15)"
                      : "rgba(229,36,36,0.1)",
                    display: "grid",
                    placeItems: "center",
                    fontWeight: 800,
                    color: theme.danger,
                    fontSize: 20,
                  }}
                >
                  !
                </div>
                <h3 style={{ margin: 0, fontSize: "1.15rem", color: darkMode ? "#e2e8f0" : "#0f172a" }}>
                  Delete this file?
                </h3>
              </div>

              <p
                style={{
                  marginTop: 0,
                  marginBottom: 16,
                  color: darkMode ? "#cbd5e1" : "#334155",
                  lineHeight: 1.4,
                }}
              >
                This action cannot be undone. The file will be removed from your
                list.
              </p>

              {pendingDelete?.type === "image" && (
                <div
                  style={{
                    background: darkMode ? "#0f172a" : "#f8fafc",
                    border: `1px solid ${theme.border}`,
                    padding: 10,
                    borderRadius: 12,
                    marginBottom: 16,
                    display: "flex",
                    alignItems: "center",
                    gap: 12,
                  }}
                >
                  <img
                    src={pendingDelete.src}
                    alt=""
                    style={{
                      width: 64,
                      height: 48,
                      objectFit: "cover",
                      borderRadius: 8,
                    }}
                  />
                  <div
                    style={{
                      color: darkMode ? "#e2e8f0" : "#475569",
                      fontSize: 14,
                      wordBreak: "break-all",
                    }}
                  >
                    {pendingDelete.name || "Untitled file"}
                  </div>
                </div>
              )}

              <div style={{ display: "flex", justifyContent: "flex-end", gap: 10 }}>
                <button
                  onClick={cancelDelete}
                  style={{
                    padding: "8px 14px",
                    borderRadius: 10,
                    border: `1px solid ${theme.border}`,
                    background: theme.panelBg,
                    color: darkMode ? "#e2e8f0" : "#0f172a",
                    fontWeight: 600,
                    cursor: "pointer",
                  }}
                >
                  Cancel
                </button>
                <button
                  onClick={confirmDelete}
                  style={{
                    padding: "8px 14px",
                    borderRadius: 10,
                    border: "none",
                    background: theme.danger,
                    color: "#ffffff",
                    fontWeight: 700,
                    cursor: "pointer",
                  }}
                >
                  Delete
                </button>
              </div>
            </MotionDiv>
          </MotionDiv>
        )}
      </AnimatePresence>

      {/* Album Detail Modal */}
      <AnimatePresence>
        {selectedAlbum && (
          <MotionDiv
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            style={{
              position: "fixed",
              top: 0,
              left: 0,
              width: "100%",
              height: "100%",
              backgroundColor: theme.overlay,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              zIndex: 1000,
              padding: "20px",
            }}
            onClick={() => setSelectedAlbum(null)}
          >
            <MotionDiv
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              transition={{ duration: 0.2 }}
              style={{
                backgroundColor: theme.panelBg,
                borderRadius: "16px",
                padding: "24px",
                maxWidth: "800px",
                maxHeight: "80vh",
                width: "100%",
                overflow: "auto",
                boxShadow: "0 10px 40px rgba(0,0,0,0.3)",
              }}
              onClick={(e) => e.stopPropagation()}
            >
              {/* Header */}
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "20px" }}>
                <h2 style={{ color: theme.primary, margin: 0 }}>
                  📁 {selectedAlbum.name}
                </h2>
                <button
                  onClick={() => setSelectedAlbum(null)}
                  style={{
                    background: "transparent",
                    border: "none",
                    color: theme.primary,
                    fontSize: "28px",
                    cursor: "pointer",
                    lineHeight: 1,
                    padding: 0,
                  }}
                >
                  ×
                </button>
              </div>

              {/* Album Info */}
              <div style={{ 
                color: theme.mutedText, 
                fontSize: "0.9rem", 
                marginBottom: "20px",
                paddingBottom: "16px",
                borderBottom: `1px solid ${theme.border}`,
              }}>
                {selectedAlbum.file_ids.length} {selectedAlbum.file_ids.length === 1 ? 'file' : 'files'}
                {selectedAlbum.created_at && (
                  <span style={{ marginLeft: "12px" }}>
                    • Created {new Date(selectedAlbum.created_at).toLocaleDateString()}
                  </span>
                )}
              </div>

              {/* Files Grid */}
              <div
                style={{
                  display: "grid",
                  gridTemplateColumns: "repeat(auto-fill, minmax(120px, 1fr))",
                  gap: "16px",
                }}
              >
                {files.filter(f => selectedAlbum.file_ids.includes(f.id)).map((file) => (
                  <div
                    key={file.id}
                    onClick={() => {
                      setSelectedAlbum(null);
                      openPreview(file);
                    }}
                    style={{
                      backgroundColor: theme.cardBg,
                      borderRadius: "10px",
                      padding: "10px",
                      cursor: "pointer",
                      textAlign: "center",
                      transition: "0.3s",
                      boxShadow: "0 2px 6px rgba(0,0,0,0.1)",
                    }}
                    onMouseOver={(e) => e.currentTarget.style.transform = "scale(1.05)"}
                    onMouseOut={(e) => e.currentTarget.style.transform = "scale(1.0)"}
                  >
                    {file.type === "image" ? (
                      <img
                        src={file.url}
                        alt={file.name}
                        style={{
                          width: "100%",
                          height: "80px",
                          objectFit: "cover",
                          borderRadius: "6px",
                          marginBottom: "8px",
                        }}
                      />
                    ) : (
                      <div
                        style={{
                          width: "100%",
                          height: "80px",
                          borderRadius: "6px",
                          backgroundColor: theme.panelBg,
                          display: "flex",
                          alignItems: "center",
                          justifyContent: "center",
                          marginBottom: "8px",
                          fontSize: "32px",
                        }}
                      >
                        {getFileIcon(file.type)}
                      </div>
                    )}
                    <div
                      style={{
                        color: theme.primary,
                        fontSize: "0.85rem",
                        fontWeight: "600",
                        overflow: "hidden",
                        textOverflow: "ellipsis",
                        whiteSpace: "nowrap",
                      }}
                    >
                      {file.name}
                    </div>
                  </div>
                ))}
              </div>
            </MotionDiv>
          </MotionDiv>
        )}
      </AnimatePresence>
    </div>
  );
}

export default App;
