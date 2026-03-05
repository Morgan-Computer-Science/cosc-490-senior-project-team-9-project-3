import React, { useEffect, useRef, useState } from "react";
import "./App.css";
import {
  createChatSession,
  fetchCourses,
  listChatMessages,
  listChatSessions,
  sendChatMessage,
} from "./api";

const Login = ({ setToken }) => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

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
        localStorage.setItem("token", data.access_token);
        setToken(data.access_token);
      } else {
        setError("Invalid username or password. Please try again.");
      }
    } catch {
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

function App() {
  const [courses, setCourses] = useState([]);
  const [token, setToken] = useState(localStorage.getItem("token"));
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
    setSessionId(null);
    setMessages([]);
    setMessageInput("");
    setChatError(null);
    setError(null);
  };

  useEffect(() => {
    if (!token) return;

    const loadDashboardData = async () => {
      setError(null);
      setChatError(null);

      try {
        const [courseData, sessions] = await Promise.all([
          fetchCourses(token),
          listChatSessions(token),
        ]);

        setCourses(courseData);

        let activeSession = sessions[0];
        if (!activeSession) {
          activeSession = await createChatSession(token, "Advising Chat");
        }

        setSessionId(activeSession.id);

        const messageData = await listChatMessages(token, activeSession.id);
        setMessages(messageData);
      } catch (err) {
        const message = err instanceof Error ? err.message : "Failed to load dashboard data.";
        setError(message);
      }
    };

    loadDashboardData();
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
            <div className="dashboard-grid">
              <section className="chat-panel">
                <h2>Advisor Chat</h2>
                {chatError && <p className="error">{chatError}</p>}

                <div className="messages-panel">
                  {messages.length === 0 && (
                    <p className="empty-chat">Ask about courses, prerequisites, or schedule planning.</p>
                  )}

                  {messages.map((msg) => (
                    <div
                      key={msg.id}
                      className={`message-bubble ${msg.sender === "assistant" ? "assistant" : "user"}`}
                    >
                      <span className="message-sender">{msg.sender === "assistant" ? "Advisor" : "You"}</span>
                      <p>{formatMessageContent(msg.content)}</p>
                    </div>
                  ))}

                  {sendingMessage && <p className="typing-indicator">Advisor is typing...</p>}
                  <div ref={messagesEndRef} />
                </div>

                <form className="chat-input-row" onSubmit={handleSendMessage}>
                  <input
                    type="text"
                    placeholder="Ask your advising question..."
                    value={messageInput}
                    onChange={(e) => setMessageInput(e.target.value)}
                    disabled={!sessionId || sendingMessage}
                  />
                  <button type="submit" disabled={!messageInput.trim() || sendingMessage || !sessionId}>
                    Send
                  </button>
                </form>
              </section>

              <section className="courses-panel">
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
              </section>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;

