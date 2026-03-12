import React, { useState, useEffect } from "react";
import "./App.css";
import Login from "./components/Login.jsx";
import Signup from "./components/Signup.jsx";
import Chatbot from "./components/Chatbot.jsx";

function App() {
  const [token, setToken] = useState(localStorage.getItem("token"));
  const [view, setView] = useState("login");
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
    const fetchCoursesData = async () => {
      try {
        const response = await fetch("http://localhost:8000/catalog/courses", {
          headers: { Authorization: `Bearer ${token}` },
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
    fetchCoursesData();
  }, [token]);

  return (
    <div className="App">
      <header className="App-header">
        <h1>AI Faculty Advisor</h1>
        {token && <button onClick={handleSignOut} className="logout-btn">Logout</button>}
      </header>
      <main>
        {!token ? (
          <div className="auth-container">
            {view === "login" ? <Login setToken={setToken} setView={setView} /> : <Signup setView={setView} />}
          </div>
        ) : (
          <div className="dashboard-grid">
            <div className="chat-section">
               <Chatbot token={token} />
            </div>
            <div className="catalog-section">
              <h3>COSC Course Catalog</h3>
              <div className="course-grid">
                {courses.map((course) => (
                  <div key={course.id} className="course-card">
                    <h4>{course.code}: {course.title}</h4>
                    <p>{course.description}</p>
                    <span>Credits: {course.credits}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;