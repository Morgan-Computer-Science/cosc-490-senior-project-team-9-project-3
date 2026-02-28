const API_BASE_URL = "http://127.0.0.1:8000";

export const fetchCourses = async (token) => {
  const response = await fetch(`${API_BASE_URL}/catalog/courses`, {
    headers: {
      'Authorization': `Bearer ${token}` // Required backend
    }
  });
  if (!response.ok) throw new Error("Failed to fetch courses");
  return response.json();
};