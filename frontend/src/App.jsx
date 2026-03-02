import React, { useState, useEffect } from "react";
import "./App.css";

// --- LOGIN COMPONENT ---
const Login = ({ setToken }) => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    // FastAPI OAuth2 expects form data, not JSON
    const formData = new FormData();
    formData.append("username", username);
    formData.append("password", password);

    try {
      const response = await fetch("http://localhost:8000/auth/login", {
        method: "POST",
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        localStorage.setItem("token", data.access_token); // Save for refresh
        setToken(data.access_token);
      } else {
        setError("Invalid username or password. Please try again.");
      }
    } catch (err) {
      setError("Cannot connect to backend. Is Uvicorn running?");
    }
  };

  return (
    <div className="login-page">
      <div className="login-card">
        <h2>MSU AI Advisor Login</h2>
        {error && <p className="error-msg">{error}</p>}
        <form onSubmit={handleSubmit}>
          <input
            type="text"
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
          <button type="submit">Sign In</button>
        </form>
      </div>
    </div>
  );
};

// --- MAIN APP COMPONENT ---
function App() {
  const [courses, setCourses] = useState([]);
  const [token, setToken] = useState(localStorage.getItem("token"));
  const [error, setError] = useState(null);

  const handleSignOut = () => {
    localStorage.removeItem("token");
    setToken(null);
    setCourses([]);
  };

  useEffect(() => {
    if (!token) return;

    const fetchCourses = async () => {
      try {
        const response = await fetch("http://localhost:8000/catalog/courses", {
          headers: {
            Authorization: `Bearer ${token}`, //
          },
        });

        if (response.status === 401) {
          throw new Error("Session expired. Please log in again.");
        }

        if (!response.ok) throw new Error("Failed to fetch courses.");

        const data = await response.json();
        setCourses(data); //
      } catch (err) {
        setError(err.message);
        console.error("Fetch error:", err);
        // handleSignOut(); // Commented out so token stays while debugging
      }
    };

    fetchCourses();
  }, [token]);

  return (
    <div className="App">
      <header className="App-header">
        <h1>Morgan State AI Faculty Advisor</h1>
        {token && (
          <button onClick={handleSignOut} className="logout-btn">
            Logout
          </button>
        )}
      </header>

      <main>
        {!token ? (
          <Login setToken={setToken} />
        ) : (
          <div className="dashboard">
            <h2>Your Academic Progress</h2>
            {error && <p className="error">{error}</p>}
            <div className="course-grid">
              {courses.map((course) => (
                <div key={course.id} className="course-card">
                  <h3>
                    {course.code}: {course.title}
                  </h3>
                  <p>{course.description}</p>
                  <span>Credits: {course.credits}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
