import React, { useState, useEffect } from "react";
import "./App.css";

// Fixes the casing error from your screenshot
import Login from "./components/Login.jsx";
import Signup from "./components/Signup.jsx";

function App() {
  const [token, setToken] = useState(localStorage.getItem("token"));
  const [view, setView] = useState("login"); // 'login' or 'signup'
  const [courses, setCourses] = useState([]);
  const [error, setError] = useState(null);

  const handleSignOut = () => {
    localStorage.removeItem("token");
    setToken(null);
    setCourses([]);
    setView("login");
  };

  useEffect(() => {
    if (!token) return;

    const fetchCourses = async () => {
      try {
        const response = await fetch("http://localhost:8000/catalog/courses", {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        if (response.ok) {
          const data = await response.json();
          setCourses(data);
        } else if (response.status === 401) {
          handleSignOut();
        }
      } catch (err) {
        setError("Failed to fetch catalog. Is the backend running?");
      }
    };

    fetchCourses();
  }, [token]);

  return (
    <div className="App">
      <header className="App-header">
        <h1>AI Advisor</h1>
        {token && (
          <button onClick={handleSignOut} className="logout-btn">
            Logout
          </button>
        )}
      </header>

      <main>
        {!token ? (
          <div className="auth-container">
            {/* Pass setView so Login and Signup can switch back and forth */}
            {view === "login" ? (
              <Login setToken={setToken} setView={setView} />
            ) : (
              <Signup setView={setView} />
            )}
          </div>
        ) : (
          <div className="dashboard">
            <h2>Welcome to your Dashboard</h2>
            <p>Authentication Successful. Course Catalog loaded below.</p>

            <section className="catalog-container">
              <h3>COSC Course Catalog</h3>
              <div className="course-grid">
                {courses.map((course) => (
                  <div key={course.id} className="course-card">
                    <h4>
                      {course.code}: {course.title}
                    </h4>
                    <p>{course.description}</p>
                    <span>Credits: {course.credits}</span>
                  </div>
                ))}
              </div>
            </section>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
