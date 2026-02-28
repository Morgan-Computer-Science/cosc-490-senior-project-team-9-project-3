import React, { useState } from "react";
import axios from "axios";
import "./Signup.css";

const Signup = ({ setView }) => {
  const [formData, setFormData] = useState({
    email: "",
    password: "",
    name: "",
    major: "Computer Science",
    year: "Freshman",
  });

  const [error, setError] = useState("");

  const handleSignup = async (e) => {
    e.preventDefault();
    setError("");

    try {
      // Hits your FastAPI register endpoint
      await axios.post("http://localhost:8000/auth/register", formData);

      alert("Registration successful! Please log in.");
      setView("login"); // Switches view back to login on success
    } catch (err) {
      const errorMsg =
        err.response?.data?.detail || "Signup failed. Please try again.";
      setError(errorMsg);
    }
  };

  return (
    <div className="login-page">
      {" "}
      {/* Reusing centered container class */}
      <div className="login-card">
        {" "}
        {/* Reusing card styling */}
        <form onSubmit={handleSignup}>
          <h2>Student Registration</h2>

          {error && (
            <p style={{ color: "#ff4d4d", fontSize: "14px" }}>{error}</p>
          )}

          <input
            type="text"
            placeholder="Full Name"
            required
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
          />

          <input
            type="email"
            placeholder="Email"
            required
            onChange={(e) =>
              setFormData({ ...formData, email: e.target.value })
            }
          />

          <input
            type="password"
            placeholder="Create Password"
            required
            onChange={(e) =>
              setFormData({ ...formData, password: e.target.value })
            }
          />

          <select
            value={formData.major}
            onChange={(e) =>
              setFormData({ ...formData, major: e.target.value })
            }
            style={{
              width: "100%",
              padding: "14px",
              marginBottom: "1rem",
              background: "#0d1117",
              color: "white",
              border: "1px solid #30363d",
              borderRadius: "6px",
            }}
          >
            <option value="Computer Science">Computer Science</option>
            <option value="Information Systems">Information Systems</option>
            <option value="Cloud Computing">Cloud Computing</option>
          </select>

          <select
            value={formData.year}
            onChange={(e) => setFormData({ ...formData, year: e.target.value })}
            style={{
              width: "100%",
              padding: "14px",
              marginBottom: "1rem",
              background: "#0d1117",
              color: "white",
              border: "1px solid #30363d",
              borderRadius: "6px",
            }}
          >
            <option value="Freshman">Freshman</option>
            <option value="Sophomore">Sophomore</option>
            <option value="Junior">Junior</option>
            <option value="Senior">Senior</option>
          </select>

          <button type="submit">Register Account</button>

          <p style={{ marginTop: "20px", color: "#8b949e", fontSize: "14px" }}>
            Already registered?{" "}
            <button
              type="button"
              onClick={() => setView("login")}
              style={{
                background: "none",
                border: "none",
                color: "#00e5ff",
                cursor: "pointer",
                textDecoration: "underline",
              }}
            >
              Log in here
            </button>
          </p>
        </form>
      </div>
    </div>
  );
};

export default Signup;
