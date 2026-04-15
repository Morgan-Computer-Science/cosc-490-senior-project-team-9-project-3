import { useEffect, useMemo, useRef, useState } from "react";

import {
  createChatSession,
  deleteChatSession,
  listChatMessages,
  listChatSessions,
  sendChatMessage,
} from "../api";

const starterPrompts = [
  "Draft a schedule for next semester",
  "Show degree requirements for my major",
  "Find the right advising office",
];

const formatMessageContent = (content) =>
  (content || "")
    .replace(/\*\*(.*?)\*\*/g, "$1")
    .replace(/^\s*[\*-]\s+/gm, "")
    .replace(/`/g, "")
    .trim();

const inferAttachmentPreview = (file, draftQuestion = "") => {
  if (!file) {
    return null;
  }

  const loweredName = file.name.toLowerCase();
  const contentType = (file.type || "").toLowerCase();
  const combined = `${loweredName} ${contentType} ${draftQuestion.toLowerCase()}`;

  if (combined.includes("audit") || combined.includes("degreeworks") || combined.includes("requirement")) {
    return "Degree audit";
  }
  if (combined.includes("transcript") || combined.includes("history") || combined.includes("grade")) {
    return "Transcript";
  }
  if (combined.includes("schedule") || combined.includes("calendar") || combined.includes("timetable")) {
    return "Schedule";
  }
  if (combined.includes("form") || combined.includes("approval") || combined.includes("registration")) {
    return "Academic form";
  }
  if (contentType.startsWith("image/")) {
    return "Screenshot";
  }
  if (loweredName.endsWith(".pdf")) {
    return "PDF";
  }
  return "Attachment";
};

const formatMessageTime = (value) => {
  if (!value) {
    return "";
  }

  try {
    return new Date(value).toLocaleTimeString([], {
      hour: "numeric",
      minute: "2-digit",
    });
  } catch {
    return "";
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
  const recognitionRef = useRef(null);
  const attachmentInputRef = useRef(null);
  const bottomRef = useRef(null);

  useEffect(() => {
    if (typeof window === "undefined") {
      return;
    }

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
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
      setListening(false);
      setVoiceStatus("Voice input was unavailable for that attempt.");
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
    return () => window.speechSynthesis.cancel();
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

  const activeTitle = sessions.find((session) => session.id === activeSessionId)?.title || "Advisor Chat";
  const attachmentPreview = inferAttachmentPreview(selectedAttachment, input);
  const groupedSessions = useMemo(() => sessions.slice(0, 5), [sessions]);

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
      if (!remaining.length) {
        const fresh = await createChatSession(token, "New advising session");
        setSessions([fresh]);
        setActiveSessionId(fresh.id);
        setMessages([]);
      } else if (activeSessionId === sessionId) {
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
      created_at: new Date().toISOString(),
    };

    setMessages((current) => [...current, optimisticMessage]);
    setInput("");
    setSending(true);
    setError("");

    try {
      const payload = await sendChatMessage(
        token,
        activeSessionId,
        text || "Please review the attached file.",
        selectedAttachment,
      );
      setMessages((current) => [
        ...current.filter((message) => message.id !== optimisticMessage.id),
        payload.user_message,
        payload.ai_message,
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
    recognitionRef.current.start();
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
      return;
    }

    synth.cancel();
    const utterance = new SpeechSynthesisUtterance(formatMessageContent(message.content));
    utterance.lang = "en-US";
    utterance.onstart = () => setSpeakingMessageId(message.id);
    utterance.onend = () => setSpeakingMessageId(null);
    utterance.onerror = () => setSpeakingMessageId(null);
    synth.speak(utterance);
  };

  const handleAttachmentPick = (event) => {
    setSelectedAttachment(event.target.files?.[0] || null);
  };

  return (
    <section className="advisor-shell">
      <div className="chat-scroll-region" id="chat-container">
        <div className="chat-column">
          <div className="date-chip">Today</div>

          <div className="session-strip">
            {groupedSessions.map((session) => (
              <button
                key={session.id}
                type="button"
                className={`session-pill ${session.id === activeSessionId ? "active" : ""}`}
                onClick={() => setActiveSessionId(session.id)}
              >
                <span>{session.title}</span>
                {groupedSessions.length > 1 ? (
                  <span
                    className="session-pill-delete"
                    onClick={(event) => {
                      event.stopPropagation();
                      handleDeleteSession(session.id);
                    }}
                  >
                    ×
                  </span>
                ) : null}
              </button>
            ))}
            <button type="button" className="session-pill add-pill" onClick={handleCreateSession}>
              + New chat
            </button>
          </div>

          {loading ? <div className="empty-note">Loading chat…</div> : null}
          {error ? <div className="error-banner">{error}</div> : null}

          {!messages.length && !loading ? (
            <div className="message-row assistant">
              <div className="avatar advisor-avatar">A</div>
              <div className="message-stack">
                <div className="message-meta">
                  <span>Advisor AI</span>
                  <span className="status-badge"><span className="status-dot" /> Ready</span>
                </div>
                <div className="message-bubble assistant-bubble">
                  <p>Hello {user?.full_name?.split(" ")[0] || "there"}, I’m your Morgan State AI Advisor.</p>
                  <p className="message-spacer">I can help with degree planning, course choices, faculty contacts, and uploaded screenshots or documents.</p>
                  <p>How can I help with your academic planning today?</p>
                </div>
              </div>
            </div>
          ) : null}

          {messages.map((message) => {
            const isAssistant = message.sender === "assistant";
            return (
              <div key={message.id} className={`message-row ${isAssistant ? "assistant" : "user"}`}>
                <div className={`avatar ${isAssistant ? "advisor-avatar" : "user-avatar"}`}>
                  {isAssistant ? "A" : (user?.full_name?.split(" ").map((part) => part[0]).join("").slice(0, 2).toUpperCase() || "MS")}
                </div>
                <div className={`message-stack ${isAssistant ? "" : "align-end"}`}>
                  <div className="message-meta">
                    <span>{isAssistant ? "Advisor AI" : "You"}</span>
                    {formatMessageTime(message.created_at) ? <span>{formatMessageTime(message.created_at)}</span> : null}
                  </div>
                  <div className={`message-bubble ${isAssistant ? "assistant-bubble" : "user-bubble"}`}>
                    {formatMessageContent(message.content).split("\n").filter(Boolean).map((line) => (
                      <p key={`${message.id}-${line}`}>{line}</p>
                    ))}
                    {isAssistant && speechSupported ? (
                      <button
                        type="button"
                        className="inline-voice-button"
                        onClick={() => handleSpeakMessage(message)}
                      >
                        {speakingMessageId === message.id ? "Stop reading" : "Read aloud"}
                      </button>
                    ) : null}
                  </div>
                </div>
              </div>
            );
          })}

          {sending ? (
            <div className="message-row assistant">
              <div className="avatar advisor-avatar">A</div>
              <div className="message-stack">
                <div className="message-meta">
                  <span>Advisor AI is typing</span>
                </div>
                <div className="typing-bubble">
                  <div className="typing-dot" />
                  <div className="typing-dot" />
                  <div className="typing-dot" />
                </div>
              </div>
            </div>
          ) : null}

          <div ref={bottomRef} />
        </div>
      </div>

      <div className="composer-wrap">
        <div className="prompt-row">
          {starterPrompts.map((prompt) => (
            <button key={prompt} type="button" className="prompt-pill" onClick={() => setInput(prompt)}>
              {prompt}
            </button>
          ))}
        </div>

        <form className="chat-composer" onSubmit={handleSend}>
          <button type="button" className="composer-icon" onClick={() => attachmentInputRef.current?.click()}>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="m21.44 11.05-9.19 9.19a6 6 0 0 1-8.49-8.49l8.57-8.57A4 4 0 1 1 18 8.84l-8.59 8.57a2 2 0 0 1-2.83-2.83l8.49-8.48" />
            </svg>
          </button>

          <textarea
            rows="1"
            value={input}
            onChange={(event) => setInput(event.target.value)}
            placeholder="Ask about courses, faculty, or degree requirements..."
          />

          <div className="composer-actions">
            <button type="button" className="composer-icon" onClick={handleVoiceInput}>
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z" />
                <path d="M19 10v2a7 7 0 0 1-14 0v-2" />
                <line x1="12" x2="12" y1="19" y2="22" />
              </svg>
            </button>
            <button type="submit" className="send-button" disabled={(!input.trim() && !selectedAttachment) || sending || !activeSessionId}>
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <line x1="22" x2="11" y1="2" y2="13" />
                <polygon points="22 2 15 22 11 13 2 9 22 2" />
              </svg>
            </button>
          </div>

          <input
            ref={attachmentInputRef}
            type="file"
            className="hidden-input"
            accept=".pdf,.txt,.md,.csv,.json,image/*"
            onChange={handleAttachmentPick}
          />
        </form>

        <div className="composer-footnote">
          {selectedAttachment ? <span>{attachmentPreview}: {selectedAttachment.name}</span> : null}
          {!selectedAttachment && voiceStatus ? <span>{voiceStatus}</span> : null}
          {!selectedAttachment && !voiceStatus ? (
            <span>AI Advisor can make mistakes. Always verify critical requirements in the official course catalog.</span>
          ) : null}
        </div>
      </div>
    </section>
  );
};

export default Chatbot;

