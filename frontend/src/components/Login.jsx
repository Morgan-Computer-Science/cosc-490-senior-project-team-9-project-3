import { useState } from "react";

import { loginUser } from "../api";

const Login = ({ setToken, setView }) => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setSubmitting(true);
    setError("");

    try {
      const data = await loginUser(email, password);
      localStorage.setItem("token", data.access_token);
      setToken(data.access_token);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="auth-shell">
      <div className="auth-card">
        <div className="auth-copy">
          <p className="eyebrow">Morgan State</p>
          <h1>Academic advising that already knows your catalog.</h1>
          <p className="auth-subtext">
            Sign in to enter a planning workspace shaped around Morgan State data,
            multimodal chat, and degree progress guidance.
          </p>
          <div className="auth-feature-stack">
            <div className="auth-feature-card">
              <span>Advisor</span>
              <strong>Grounded replies across courses, departments, and support resources.</strong>
            </div>
            <div className="auth-feature-card">
              <span>Planning</span>
              <strong>Track completed courses, import records, and see what is ready next.</strong>
            </div>
            <div className="auth-feature-card">
              <span>Multimodal</span>
              <strong>Use voice, screenshots, PDFs, and text files inside the same advising flow.</strong>
            </div>
          </div>
        </div>

        <form className="auth-form" onSubmit={handleSubmit}>
          <h2>Welcome back</h2>
          {error ? <p className="form-error">{error}</p> : null}

          <label>
            Email
            <input
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              placeholder="student@morgan.edu"
              required
            />
          </label>

          <label>
            Password
            <input
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              placeholder="Your password"
              required
            />
          </label>

          <button type="submit" disabled={submitting}>
            {submitting ? "Signing in..." : "Sign in"}
          </button>
        </form>

        <p className="auth-switch">
          Need an account?
          <button type="button" className="link-button" onClick={() => setView("signup")}>
            Create one
          </button>
        </p>
      </div>
    </div>
  );
};

export default Login;
