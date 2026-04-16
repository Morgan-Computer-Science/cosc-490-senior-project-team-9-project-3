const API_BASE_URL = "http://127.0.0.1:8000";

const authHeaders = (token) => ({
  Authorization: `Bearer ${token}`,
});

async function parseResponse(response, fallbackMessage) {
  const isJson = response.headers.get("content-type")?.includes("application/json");
  const payload = isJson ? await response.json() : null;

  if (!response.ok) {
    throw new Error(payload?.detail || fallbackMessage);
  }

  return payload;
}

export async function loginUser(email, password) {
  const formData = new FormData();
  formData.append("username", email);
  formData.append("password", password);

  const response = await fetch(`${API_BASE_URL}/auth/login`, {
    method: "POST",
    body: formData,
  });

  return parseResponse(response, "Login failed.");
}

export async function registerUser(formData) {
  const response = await fetch(`${API_BASE_URL}/auth/register`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(formData),
  });

  return parseResponse(response, "Registration failed.");
}

export async function fetchCurrentUser(token) {
  const response = await fetch(`${API_BASE_URL}/auth/me`, {
    headers: authHeaders(token),
  });

  return parseResponse(response, "Failed to load profile.");
}

export async function updateCurrentUser(token, updates) {
  const response = await fetch(`${API_BASE_URL}/auth/me`, {
    method: "PUT",
    headers: {
      ...authHeaders(token),
      "Content-Type": "application/json",
    },
    body: JSON.stringify(updates),
  });

  return parseResponse(response, "Failed to update profile.");
}

export async function updateCompletedCourses(token, courseCodes, importPreview = null) {
  const response = await fetch(`${API_BASE_URL}/auth/me/completed-courses`, {
    method: "PUT",
    headers: {
      ...authHeaders(token),
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ course_codes: courseCodes, import_preview: importPreview }),
  });

  return parseResponse(response, "Failed to update completed courses.");
}

export async function importCompletedCourses(
  token,
  sourceText = "",
  attachment = null,
  importSource = "manual",
) {
  const formData = new FormData();
  formData.append("import_source", importSource);
  formData.append("source_text", sourceText);
  if (attachment) {
    formData.append("attachment", attachment);
  }

  const response = await fetch(`${API_BASE_URL}/auth/me/completed-courses/import`, {
    method: "POST",
    headers: authHeaders(token),
    body: formData,
  });

  return parseResponse(response, "Failed to import completed courses.");
}

export async function fetchDegreeProgress(token) {
  const response = await fetch(`${API_BASE_URL}/auth/me/degree-progress`, {
    headers: authHeaders(token),
  });

  return parseResponse(response, "Failed to load degree progress.");
}

export async function fetchCourses(token, filters = {}) {
  const params = new URLSearchParams();

  if (filters.search?.trim()) {
    params.set("search", filters.search.trim());
  }
  if (filters.level?.trim()) {
    params.set("level", filters.level.trim());
  }
  if (filters.major?.trim()) {
    params.set("major", filters.major.trim());
  }

  const query = params.toString();
  const response = await fetch(
    `${API_BASE_URL}/catalog/courses${query ? `?${query}` : ""}`,
    {
      headers: authHeaders(token),
    },
  );

  return parseResponse(response, "Failed to fetch courses.");
}

export async function fetchDepartments(token) {
  const response = await fetch(`${API_BASE_URL}/catalog/departments`, {
    headers: authHeaders(token),
  });

  return parseResponse(response, "Failed to fetch departments.");
}

export async function fetchFaculty(token) {
  const response = await fetch(`${API_BASE_URL}/catalog/faculty`, {
    headers: authHeaders(token),
  });

  return parseResponse(response, "Failed to fetch faculty.");
}

export async function fetchSupportResources(token) {
  const response = await fetch(`${API_BASE_URL}/catalog/support-resources`, {
    headers: authHeaders(token),
  });

  return parseResponse(response, "Failed to fetch support resources.");
}

export async function fetchConnectors(token) {
  const response = await fetch(`${API_BASE_URL}/integrations/connectors`, {
    headers: authHeaders(token),
  });

  return parseResponse(response, "Failed to fetch connectors.");
}

export async function listChatSessions(token) {
  const response = await fetch(`${API_BASE_URL}/chat/sessions`, {
    headers: authHeaders(token),
  });

  return parseResponse(response, "Failed to fetch chat sessions.");
}

export async function createChatSession(token, title = "New advising session") {
  const response = await fetch(`${API_BASE_URL}/chat/sessions`, {
    method: "POST",
    headers: {
      ...authHeaders(token),
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ title }),
  });

  return parseResponse(response, "Failed to create chat session.");
}

export async function deleteChatSession(token, sessionId) {
  const response = await fetch(`${API_BASE_URL}/chat/sessions/${sessionId}`, {
    method: "DELETE",
    headers: authHeaders(token),
  });

  if (!response.ok) {
    throw new Error("Failed to delete chat session.");
  }
}

export async function listChatMessages(token, sessionId) {
  const response = await fetch(`${API_BASE_URL}/chat/sessions/${sessionId}/messages`, {
    headers: authHeaders(token),
  });

  return parseResponse(response, "Failed to fetch chat messages.");
}

export async function sendChatMessage(token, sessionId, content, attachment = null) {
  const formData = new FormData();
  formData.append("content", content);
  if (attachment) {
    formData.append("attachment", attachment);
  }

  const response = await fetch(`${API_BASE_URL}/chat/sessions/${sessionId}/messages`, {
    method: "POST",
    headers: {
      ...authHeaders(token),
    },
    body: formData,
  });

  return parseResponse(response, "Failed to send message.");
}
