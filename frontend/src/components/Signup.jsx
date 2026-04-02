import { useState } from "react";

import { registerUser } from "../api";
import { majorOptions } from "../majors";

const Signup = ({ setView }) => {
  const [formData, setFormData] = useState({
    full_name: "",
    email: "",
    password: "",
    major: "Computer Science",
    year: "Freshman",
  });
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const updateField = (field, value) => {
    setFormData((current) => ({ ...current, [field]: value }));
  };

  const handleSignup = async (event) => {
    event.preventDefault();
    setSubmitting(true);
    setError("");
    setSuccess("");

    try {
      await registerUser(formData);
      setSuccess("Registration complete. You can sign in now.");
      setView("login");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Signup failed.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="auth-shell">
      <div className="auth-card">
        <div className="auth-copy">
          <p className="eyebrow">Student Onboarding</p>
          <h1>Build a profile the advisor can actually use.</h1>
          <p className="auth-subtext">
            Your major and class year help the advisor retrieve the right Morgan State guidance.
          </p>
          <div className="auth-feature-stack">
            <div className="auth-feature-card">
              <span>Profile grounding</span>
              <strong>Major and year shape advising context from the first conversation.</strong>
            </div>
            <div className="auth-feature-card">
              <span>Progress engine</span>
              <strong>Prerequisite-aware recommendations are based on what you have already completed.</strong>
            </div>
            <div className="auth-feature-card">
              <span>Connector ready</span>
              <strong>Transcript, Canvas-style, and WebSIS-style imports already fit the workflow.</strong>
            </div>
          </div>
        </div>

        <form className="auth-form" onSubmit={handleSignup}>
          <h2>Create account</h2>
          {error ? <p className="form-error">{error}</p> : null}
          {success ? <p className="form-success">{success}</p> : null}

          <label>
            Full name
            <input
              type="text"
              value={formData.full_name}
              onChange={(event) => updateField("full_name", event.target.value)}
              placeholder="Jordan Smith"
              required
            />
          </label>

          <label>
            Email
            <input
              type="email"
              value={formData.email}
              onChange={(event) => updateField("email", event.target.value)}
              placeholder="student@morgan.edu"
              required
            />
          </label>

          <label>
            Password
            <input
              type="password"
              value={formData.password}
              onChange={(event) => updateField("password", event.target.value)}
              placeholder="At least 8 characters"
              required
            />
          </label>

          <label>
            Major
            <select
              value={formData.major}
              onChange={(event) => updateField("major", event.target.value)}
            >
              {majorOptions.map((major) => (
                <option key={major} value={major}>
                  {major}
                </option>
              ))}
            </select>
          </label>

          <label>
            Class year
            <select
              value={formData.year}
              onChange={(event) => updateField("year", event.target.value)}
            >
              <option value="Freshman">Freshman</option>
              <option value="Sophomore">Sophomore</option>
              <option value="Junior">Junior</option>
              <option value="Senior">Senior</option>
            </select>
          </label>

          <button type="submit" disabled={submitting}>
            {submitting ? "Creating..." : "Create account"}
          </button>
        </form>

        <p className="auth-switch">
          Already registered?
          <button type="button" className="link-button" onClick={() => setView("login")}>
            Sign in
          </button>
        </p>
      </div>
    </div>
  );
};

export default Signup;
