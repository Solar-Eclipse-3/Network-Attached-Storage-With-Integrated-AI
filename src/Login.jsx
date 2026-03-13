import { useState } from "react";
import { auth } from "./firebase";
import { signInWithEmailAndPassword } from "firebase/auth";

function Login({ setUserEmail }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState(""); // store success/error message
  const [messageType, setMessageType] = useState(""); // "success" or "error"

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const userCredential = await signInWithEmailAndPassword(auth, email, password);
      console.log("Logged in successfully:", userCredential.user);
      
      // Show success message instead of alert
      setMessage("Login successful!");
      setMessageType("success");

      setUserEmail(email); // set logged-in user in App
      setEmail("");
      setPassword("");

      // Clear message after 3 seconds
      setTimeout(() => setMessage(""), 3000);
    } catch (error) {
      console.error("Login error:", error.message);

      // Show error message
      setMessage("Error: " + error.message);
      setMessageType("error");

      // Clear message after 5 seconds
      setTimeout(() => setMessage(""), 5000);
    }
  };

  return (
    <form onSubmit={handleLogin} style={{ marginTop: "20px", display: "flex", flexDirection: "column", gap: "10px" }}>
      {message && (
        <div
          style={{
            color: messageType === "success" ? "#1dd1a1" : "#ff6b6b",
            fontWeight: "bold",
            textAlign: "center",
          }}
        >
          {message}
        </div>
      )}
      <input
        type="email"
        placeholder="Email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        required
        style={{ padding: "8px", borderRadius: "10px", border: "1px solid #333", backgroundColor: "#1f1f1f", color: "white" }}
      />
      <input
        type="password"
        placeholder="Password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        required
        style={{ padding: "8px", borderRadius: "10px", border: "1px solid #333", backgroundColor: "#1f1f1f", color: "white" }}
      />
      <button
        type="submit"
        style={{
          padding: "8px",
          borderRadius: "10px",
          border: "none",
          backgroundColor: "#54a0ff",
          color: "white",
          fontWeight: "bold",
          cursor: "pointer",
          transition: "0.3s",
        }}
        onMouseOver={(e) => (e.target.style.backgroundColor = "#2e86de")}
        onMouseOut={(e) => (e.target.style.backgroundColor = "#54a0ff")}
      >
        Login
      </button>
    </form>
  );
}

export default Login;
