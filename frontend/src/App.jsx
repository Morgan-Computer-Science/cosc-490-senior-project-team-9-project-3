import React, { useEffect, useRef, useState } from "react";
import "./App.css";
import Login from "./components/Login.jsx";
import Signup from "./components/Signup.jsx";
import Chatbot from "./components/Chatbot.jsx"; // New Component

function App() {
  const [token, setToken] = useState(localStorage.getItem("token"));
  const [view, setView] = useState("login");
  const [courses, setCourses] = useState([]);
  const [error, setError] = useState(null);

  const [sessionId, setSessionId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [messageInput, setMessageInput] = useState("");
  const [chatError, setChatError] = useState(null);
  const [sendingMessage, setSendingMessage] = useState(false);
  const messagesEndRef = useRef(null);

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

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const formatMessageContent = (content) => {
    if (!content) return "";
    return content
      .replace(/\*\*(.*?)\*\*/g, "$1")
      .replace(/^\s*[\*-]\s+/gm, "")
      .replace(/`/g, "");
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!sessionId || !messageInput.trim() || sendingMessage) return;

    const text = messageInput.trim();
    setMessageInput("");
    setSendingMessage(true);
    setChatError(null);

    try {
      const payload = await sendChatMessage(token, sessionId, text);

      setMessages((prev) => [
        ...prev,
        payload.user_message,
        payload.ai_message,
      ]);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to send message.";
      setChatError(message);
      setMessages((prev) => [
        ...prev,
        {
          id: `local-${Date.now()}`,
          sender: "assistant",
          content: "I could not process that right now. Please try again.",
        },
      ]);
    } finally {
      setSendingMessage(false);
    }
  };

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
