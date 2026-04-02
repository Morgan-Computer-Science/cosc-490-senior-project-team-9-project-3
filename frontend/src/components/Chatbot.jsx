import { useEffect, useRef, useState } from "react";

import {
  createChatSession,
  deleteChatSession,
  listChatMessages,
  listChatSessions,
  sendChatMessage,
} from "../api";

const starterPrompts = [
  "Help me plan a strong sophomore schedule.",
  "What classes should I take after COSC 111?",
  "Who should I contact for Information Systems advising?",
  "What are the degree requirements for Business Administration?",
  "I feel overwhelmed and need help finding the right campus support.",
  "How should I prepare for internships in my major?",
  "Can you review this screenshot or schedule image and tell me what matters for advising?",
];

const formatMessageContent = (content) =>
  (content || "")
    .replace(/\*\*(.*?)\*\*/g, "$1")
    .replace(/^\s*[\*-]\s+/gm, "")
    .replace(/`/g, "")
    .trim();

const formatMessageTime = (value) => {
  if (!value) {
    return "Just now";
  }

  try {
    return new Date(value).toLocaleTimeString([], {
      hour: "numeric",
      minute: "2-digit",
    });
  } catch {
    return "Just now";
  }
};

const Chatbot = ({ token, user }) => {
  const [sessions, setSessions] = useState([]);
  const [activeSessionId, setActiveSessionId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState("");
  const [voiceSupported, setVoiceSupported] = useState(false);
  const [listening, setListening] = useState(false);
  const [voiceStatus, setVoiceStatus] = useState("");
  const [speechSupported, setSpeechSupported] = useState(false);
  const [speakingMessageId, setSpeakingMessageId] = useState(null);
  const [selectedAttachment, setSelectedAttachment] = useState(null);
  const bottomRef = useRef(null);
  const recognitionRef = useRef(null);
  const attachmentInputRef = useRef(null);

  useEffect(() => {
    if (typeof window === "undefined") {
      return;
    }

    const SpeechRecognition =
      window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
      setVoiceSupported(false);
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = "en-US";

    recognition.onstart = () => {
      setListening(true);
      setVoiceStatus("Listening...");
    };

    recognition.onresult = (event) => {
      const transcript = event.results?.[0]?.[0]?.transcript?.trim();
      if (transcript) {
        setInput((current) => (current ? `${current} ${transcript}` : transcript));
        setVoiceStatus("Voice captured.");
      }
    };

    recognition.onerror = () => {
      setVoiceStatus("Voice input was unavailable for that attempt.");
      setListening(false);
    };

    recognition.onend = () => {
      setListening(false);
    };

    recognitionRef.current = recognition;
    setVoiceSupported(true);

    return () => {
      recognition.stop();
    };
  }, []);

  useEffect(() => {
    if (typeof window === "undefined" || !window.speechSynthesis) {
      setSpeechSupported(false);
      return undefined;
    }

    setSpeechSupported(true);

    return () => {
      window.speechSynthesis.cancel();
    };
  }, []);

  useEffect(() => {
    if (!token) {
      return;
    }

    const initialize = async () => {
      setLoading(true);
      setError("");

      try {
        const currentSessions = await listChatSessions(token);
        const nextSessions = currentSessions.length
          ? currentSessions
          : [await createChatSession(token, "New advising session")];

        setSessions(nextSessions);
        setActiveSessionId(nextSessions[0].id);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Unable to load advisor chat.");
      } finally {
        setLoading(false);
      }
    };

    initialize();
  }, [token]);

  useEffect(() => {
    if (!token || !activeSessionId) {
      return;
    }

    const loadMessages = async () => {
      try {
        const sessionMessages = await listChatMessages(token, activeSessionId);
        setMessages(sessionMessages);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Unable to load messages.");
      }
    };

    loadMessages();
  }, [token, activeSessionId]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, sending]);

  const handleCreateSession = async () => {
    try {
      const nextSession = await createChatSession(token, "New advising session");
      setSessions((current) => [nextSession, ...current]);
      setActiveSessionId(nextSession.id);
      setMessages([]);
      setInput("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to create session.");
    }
  };

  const handleDeleteSession = async (sessionId) => {
    try {
      await deleteChatSession(token, sessionId);
      const remaining = sessions.filter((session) => session.id !== sessionId);
      setSessions(remaining);

      if (remaining.length === 0) {
        const freshSession = await createChatSession(token, "New advising session");
        setSessions([freshSession]);
        setActiveSessionId(freshSession.id);
        setMessages([]);
        return;
      }

      if (activeSessionId === sessionId) {
        setActiveSessionId(remaining[0].id);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to delete session.");
    }
  };

  const handleSend = async (event) => {
    event?.preventDefault();
    if ((!input.trim() && !selectedAttachment) || !activeSessionId || sending) {
      return;
    }

    const text = input.trim();
    const optimisticMessage = {
      id: `local-user-${Date.now()}`,
      sender: "user",
      content: selectedAttachment ? `${text}\n\nAttachment: ${selectedAttachment.name}`.trim() : text,
    };

    setMessages((current) => [...current, optimisticMessage]);
    setInput("");
    setSending(true);
    setError("");

    try {
      const payload = await sendChatMessage(token, activeSessionId, text || "Please review the attached file.", selectedAttachment);
      setMessages((current) => [
        ...current.filter((message) => message.id !== optimisticMessage.id),
        payload.user_message,
        { ...payload.ai_message, advisor_insights: payload.advisor_insights },
      ]);
      setSelectedAttachment(null);
      if (attachmentInputRef.current) {
        attachmentInputRef.current.value = "";
      }

      setSessions((current) =>
        current.map((session) =>
          session.id === activeSessionId
            ? { ...session, title: payload.user_message.content.slice(0, 40) || session.title }
            : session,
        ),
      );
    } catch (err) {
      setMessages((current) => current.filter((message) => message.id !== optimisticMessage.id));
      setError(err instanceof Error ? err.message : "Unable to send message.");
    } finally {
      setSending(false);
    }
  };

  const handleVoiceInput = () => {
    if (!recognitionRef.current) {
      setVoiceStatus("Voice input is not supported in this browser.");
      return;
    }

    if (listening) {
      recognitionRef.current.stop();
      return;
    }

    setError("");
    setVoiceStatus("");
    recognitionRef.current.start();
  };

  const handleAttachmentPick = (event) => {
    const nextFile = event.target.files?.[0] || null;
    setSelectedAttachment(nextFile);
    setError("");
  };

  const handleSpeakMessage = (message) => {
    if (!speechSupported || typeof window === "undefined") {
      setVoiceStatus("Spoken replies are not supported in this browser.");
      return;
    }

    const synth = window.speechSynthesis;
    if (speakingMessageId === message.id) {
      synth.cancel();
      setSpeakingMessageId(null);
      setVoiceStatus("Stopped reading aloud.");
      return;
    }

    synth.cancel();

    const utterance = new SpeechSynthesisUtterance(formatMessageContent(message.content));
    utterance.lang = "en-US";
    utterance.rate = 1;
    utterance.onstart = () => {
      setSpeakingMessageId(message.id);
      setVoiceStatus("Reading advisor response aloud...");
    };
    utterance.onend = () => {
      setSpeakingMessageId(null);
      setVoiceStatus("Finished reading response.");
    };
    utterance.onerror = () => {
      setSpeakingMessageId(null);
      setVoiceStatus("Spoken playback was unavailable for that reply.");
    };
    synth.speak(utterance);
  };

  const activeTitle = sessions.find((session) => session.id === activeSessionId)?.title;

  return (
    <section className="panel advisor-panel">
      <div className="panel-header">
        <div>
          <p className="eyebrow">Advisor Workspace</p>
          <h2>{activeTitle || "Academic advisor chat"}</h2>
          <p className="panel-subtext">
            Built for {user?.major || "Morgan State students"} and grounded in Morgan State advising data.
          </p>
          <p className="panel-subtext">
            You can also upload screenshots, PDFs, or text files for multimodal advising.
          </p>
        </div>
        <div className="chat-header-actions">
          <div className="chat-status-pill">
            <span>Mode</span>
            <strong>{selectedAttachment ? "Multimodal" : "Advising chat"}</strong>
          </div>
          <button type="button" className="secondary-button" onClick={handleCreateSession}>
            New chat
          </button>
        </div>
      </div>

      <div className="chat-layout">
        <aside className="session-list">
          <div className="session-list-header">
            <p className="eyebrow">Sessions</p>
            <span>{sessions.length} active</span>
          </div>
          {sessions.map((session) => (
            <div
              key={session.id}
              className={`session-card ${session.id === activeSessionId ? "active" : ""}`}
            >
              <button type="button" className="session-select" onClick={() => setActiveSessionId(session.id)}>
                <strong>{session.title}</strong>
                <span>{new Date(session.created_at).toLocaleDateString()}</span>
              </button>
              <button
                type="button"
                className="session-delete"
                onClick={() => handleDeleteSession(session.id)}
                aria-label={`Delete ${session.title}`}
              >
                x
              </button>
            </div>
          ))}
        </aside>

        <div className="chat-column">
          <div className="chat-surface-intro">
            <div className="hero-badges">
              <span className="hero-chip">Context aware</span>
              <span className="hero-chip">Support aware</span>
              <span className="hero-chip">Voice + file input</span>
            </div>
          </div>
          <div className="starter-row">
            {starterPrompts.map((prompt) => (
              <button key={prompt} type="button" className="starter-pill" onClick={() => setInput(prompt)}>
                {prompt}
              </button>
            ))}
          </div>

          <div className="messages-panel">
            {loading ? <p className="empty-state">Loading your advisor workspace...</p> : null}
            {!loading && messages.length === 0 ? (
              <p className="empty-state">
                Ask about schedules, faculty, department contacts, requirements, internships, or support resources.
              </p>
            ) : null}

            {messages.map((message) => (
              <div
                key={message.id}
                className={`message-bubble ${message.sender === "assistant" ? "assistant" : "user"}`}
              >
                <div className="message-meta">
                  <span className="message-sender">
                    {message.sender === "assistant" ? "Advisor" : "You"}
                  </span>
                  <span className="message-time">{formatMessageTime(message.created_at)}</span>
                </div>
                <p>{formatMessageContent(message.content)}</p>
                {message.sender === "assistant" && speechSupported ? (
                  <button
                    type="button"
                    className="listen-button"
                    onClick={() => handleSpeakMessage(message)}
                  >
                    {speakingMessageId === message.id ? "Stop audio" : "Read aloud"}
                  </button>
                ) : null}
              </div>
            ))}

            {sending ? <p className="typing-indicator">Advisor is thinking...</p> : null}
            {voiceStatus ? <p className="typing-indicator">{voiceStatus}</p> : null}
            {error ? <p className="form-error">{error}</p> : null}
            <div ref={bottomRef} />
          </div>

          <form className="chat-input-row" onSubmit={handleSend}>
            <input
              value={input}
              onChange={(event) => setInput(event.target.value)}
              placeholder="Ask about requirements, advising offices, professors, course planning, or an attached file..."
              disabled={!activeSessionId || sending}
            />
            <label className="upload-button">
              Add file
              <input
                ref={attachmentInputRef}
                type="file"
                accept=".pdf,.txt,.md,.csv,.json,image/*"
                onChange={handleAttachmentPick}
                disabled={sending}
              />
            </label>
            <button
              type="submit"
              disabled={(!input.trim() && !selectedAttachment) || sending || !activeSessionId}
            >
              {sending ? "Sending..." : "Send"}
            </button>
            <button
              type="button"
              className="voice-button"
              onClick={handleVoiceInput}
              disabled={!voiceSupported}
            >
              {listening ? "Stop mic" : "Use mic"}
            </button>
          </form>
          <div className="composer-footnote">
            <span>Tip</span>
            <p>Use screenshots for schedule reviews, PDFs for audits, or voice input for quick advising questions.</p>
          </div>
          {selectedAttachment ? (
            <p className="attachment-pill">
              Ready to send: {selectedAttachment.name}. Images and PDFs now go through multimodal analysis.
            </p>
          ) : null}
        </div>
      </div>
    </section>
  );
};

export default Chatbot;
