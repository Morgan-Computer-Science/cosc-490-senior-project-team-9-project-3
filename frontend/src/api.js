const API_BASE_URL = "http://127.0.0.1:8000";

// --- Catalog Functions ---
export const fetchCourses = async (token) => {
  const response = await fetch(`${API_BASE_URL}/catalog/courses`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
  if (!response.ok) throw new Error("Failed to fetch courses");
  return response.json();
};

// --- Chat Functions ---
export const createChatSession = async (
  token,
  title = "New Advising Session",
) => {
  const response = await fetch(`${API_BASE_URL}/chat/sessions`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ title }),
  });
  if (!response.ok) throw new Error("Failed to create chat session");
  return response.json();
};

export const sendChatMessage = async (token, sessionId, content) => {
  const response = await fetch(
    `${API_BASE_URL}/chat/sessions/${sessionId}/messages`,
    {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ content }),
    },
  );
  if (!response.ok) throw new Error("Failed to send message");
  return response.json();
};
