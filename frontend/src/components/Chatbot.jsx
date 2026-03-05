import React, { useState, useEffect, useRef } from "react";
import { createChatSession, sendChatMessage } from "../api";

const Chatbot = ({ token }) => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [sessionId, setSessionId] = useState(null);
  const chatEndRef = useRef(null);

  useEffect(() => {
    const initSession = async () => {
      try {
        const data = await createChatSession(token);
        setSessionId(data.id);
      } catch (err) {
        console.error("Session init failed", err);
      }
    };
    if (token) initSession();
  }, [token]);

  const handleSend = async () => {
    if (!input.trim() || !sessionId) return;
    
    const userMsg = { sender: "user", content: input };
    setMessages(prev => [...prev, userMsg]);
    setInput("");

    try {
      const data = await sendChatMessage(token, sessionId, input);
      setMessages(prev => [...prev, data.ai_message]);
    } catch (err) {
      console.error("Chat error", err);
    }
  };

  return (
    <div className="chatbot-container">
      <h3>Academic Advisor Chat</h3>
      <div className="chat-window">
        {messages.map((m, i) => (
          <div key={i} className={`message ${m.sender}`}>
            <strong>{m.sender === "user" ? "You" : "Advisor"}:</strong> {m.content}
          </div>
        ))}
        <div ref={chatEndRef} />
      </div>
      <div className="chat-input-area">
        <input 
          value={input} 
          onChange={(e) => setInput(e.target.value)} 
          onKeyPress={(e) => e.key === 'Enter' && handleSend()}
          placeholder="Ask me anything about your degree..." 
        />
        <button onClick={handleSend}>Send</button>
        <button className="mic-btn" title="Audio coming soon">🎤</button>
      </div>
    </div>
  );
};

export default Chatbot;