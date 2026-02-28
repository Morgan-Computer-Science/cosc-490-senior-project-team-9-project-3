import React, { useState } from "react";
import "./Login.css";

const Login = ({ setToken, setView }) => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();

    const formData = new FormData();
    formData.append("username", email);
    formData.append("password", password);

    try {
      const response = await fetch("http://localhost:8000/auth/login", {
        method: "POST",
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        localStorage.setItem("token", data.access_token);
        setToken(data.access_token);
      } else {
        alert("Invalid credentials. Check your email and password.");
      }
    } catch (err) {
      console.error("Login failed:", err);
      alert("Cannot connect to server.");
    }
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <h2>AI Faculty Advisor Login</h2>
        <form onSubmit={handleSubmit}>
          <input
            type="text"
            placeholder="Email"
            onChange={(e) => setEmail(e.target.value)}
            required
          />
          <input
            type="password"
            placeholder="Password"
            onChange={(e) => setPassword(e.target.value)}
            required
          />
          <button type="submit">Login</button>
        </form>

        {/* Toggle to Signup View */}
        <p style={{ marginTop: "15px", fontSize: "14px" }}>
          Don't have an account?{" "}
          <button
            onClick={() => setView("signup")}
            style={{
              background: "none",
              border: "none",
              color: "#002D72",
              cursor: "pointer",
              textDecoration: "underline",
            }}
          >
            Sign Up here
          </button>
        </p>
      </div>
    </div>
  );
};

export default Login;
