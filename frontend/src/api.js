const API_BASE_URL = "http://127.0.0.1:8000";

const authHeaders = (token) => ({
  Authorization: `Bearer ${token}`,
});

export const fetchCourses = async (token) => {
  const response = await fetch(`${API_BASE_URL}/catalog/courses`, {
    headers: authHeaders(token),
  });
  if (!response.ok) throw new Error("Failed to fetch courses");
  return response.json();
};

export const listChatSessions = async (token) => {
  const response = await fetch(`${API_BASE_URL}/chat/sessions`, {
    headers: authHeaders(token),
  });
  if (!response.ok) throw new Error("Failed to fetch chat sessions");
  return response.json();
};

export const createChatSession = async (token, title = "New advising session") => {
  const response = await fetch(`${API_BASE_URL}/chat/sessions`, {
    method: "POST",
    headers: {
      ...authHeaders(token),
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ title }),
  });
  if (!response.ok) throw new Error("Failed to create chat session");
  return response.json();
};

export const listChatMessages = async (token, sessionId) => {
  const response = await fetch(`${API_BASE_URL}/chat/sessions/${sessionId}/messages`, {
    headers: authHeaders(token),
  });
  if (!response.ok) throw new Error("Failed to fetch chat messages");
  return response.json();
};

export const sendChatMessage = async (token, sessionId, content) => {
  const response = await fetch(`${API_BASE_URL}/chat/sessions/${sessionId}/messages`, {
    method: "POST",
    headers: {
      ...authHeaders(token),
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ content }),
  });
  if (!response.ok) throw new Error("Failed to send message");
  return response.json();
};
