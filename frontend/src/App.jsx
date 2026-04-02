import { startTransition, useDeferredValue, useEffect, useState } from "react";

import "./App.css";
import {
  fetchCourses,
  fetchDegreeProgress,
  fetchCurrentUser,
  importCompletedCourses,
  updateCompletedCourses,
  updateCurrentUser,
} from "./api";
import Chatbot from "./components/Chatbot.jsx";
import Login from "./components/Login.jsx";
import ProfilePanel from "./components/ProfilePanel.jsx";
import Signup from "./components/Signup.jsx";

const levels = [
  { label: "All levels", value: "" },
  { label: "100 level", value: "1" },
  { label: "200 level", value: "2" },
  { label: "300 level", value: "3" },
  { label: "400 level", value: "4" },
];

const tabs = [
  { id: "advisor", label: "Advisor" },
  { id: "catalog", label: "Catalog" },
  { id: "profile", label: "Profile" },
];

function App() {
  const [token, setToken] = useState(localStorage.getItem("token"));
  const [authView, setAuthView] = useState("login");
  const [activeTab, setActiveTab] = useState("advisor");
  const [user, setUser] = useState(null);
  const [courses, setCourses] = useState([]);
  const [searchText, setSearchText] = useState("");
  const [selectedLevel, setSelectedLevel] = useState("");
  const [loadingCourses, setLoadingCourses] = useState(false);
  const [loadingProfile, setLoadingProfile] = useState(false);
  const [savingProfile, setSavingProfile] = useState(false);
  const [degreeProgress, setDegreeProgress] = useState(null);
  const [error, setError] = useState("");
  const deferredSearch = useDeferredValue(searchText);

  useEffect(() => {
    if (!token) {
      return;
    }

    const loadProfile = async () => {
      setLoadingProfile(true);
      setError("");

      try {
        const profile = await fetchCurrentUser(token);
        startTransition(() => setUser(profile));
      } catch (err) {
        localStorage.removeItem("token");
        setToken(null);
        setError(err instanceof Error ? err.message : "Session expired.");
      } finally {
        setLoadingProfile(false);
      }
    };

    loadProfile();
  }, [token]);

  useEffect(() => {
    if (!token) {
      return;
    }

    const loadDegreeProgress = async () => {
      try {
        const summary = await fetchDegreeProgress(token);
        startTransition(() => setDegreeProgress(summary));
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load degree progress.");
      }
    };

    loadDegreeProgress();
  }, [token, user?.major, user?.completed_courses?.length]);

  useEffect(() => {
    if (!token) {
      return;
    }

    const loadCourses = async () => {
      setLoadingCourses(true);

      try {
        const nextCourses = await fetchCourses(token, {
          search: deferredSearch,
          level: selectedLevel,
        });
        startTransition(() => setCourses(nextCourses));
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load courses.");
      } finally {
        setLoadingCourses(false);
      }
    };

    loadCourses();
  }, [token, deferredSearch, selectedLevel]);

  const handleSignOut = () => {
    localStorage.removeItem("token");
    setToken(null);
    setUser(null);
    setCourses([]);
    setSearchText("");
    setSelectedLevel("");
    setActiveTab("advisor");
    setAuthView("login");
    setError("");
  };

  const handleSaveProfile = async (updates) => {
    if (!token) {
      throw new Error("You are signed out.");
    }

    setSavingProfile(true);
    try {
      const nextUser = await updateCurrentUser(token, updates);
      setUser(nextUser);
      const nextSummary = await fetchDegreeProgress(token);
      setDegreeProgress(nextSummary);
      return nextUser;
    } finally {
      setSavingProfile(false);
    }
  };

  const handleSaveCompletedCourses = async (courseCodes) => {
    if (!token || !user) {
      throw new Error("You are signed out.");
    }

    setSavingProfile(true);
    try {
      const completedCourses = await updateCompletedCourses(token, courseCodes);
      setUser((current) => (current ? { ...current, completed_courses: completedCourses } : current));
      const nextSummary = await fetchDegreeProgress(token);
      setDegreeProgress(nextSummary);
      return completedCourses;
    } finally {
      setSavingProfile(false);
    }
  };

  const handleImportCompletedCourses = async (sourceText, attachment, importSource) => {
    if (!token) {
      throw new Error("You are signed out.");
    }

    return importCompletedCourses(token, sourceText, attachment, importSource);
  };

  if (!token) {
    return authView === "login" ? (
      <Login setToken={setToken} setView={setAuthView} />
    ) : (
      <Signup setView={setAuthView} />
    );
  }

  return (
    <div className="app-shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">COSC 490 Senior Project</p>
          <h1>Morgan State AI Faculty Advisor</h1>
        </div>

        <div className="topbar-actions">
          <div className="student-chip">
            <strong>{user?.full_name || "Student"}</strong>
            <span>{user?.major || "Major not set"}</span>
          </div>
          <button type="button" className="secondary-button" onClick={handleSignOut}>
            Logout
          </button>
        </div>
      </header>

      <main className="workspace">
        <aside className="sidebar">
          <div className="sidebar-card">
            <p className="eyebrow">Navigation</p>
            {tabs.map((tab) => (
              <button
                key={tab.id}
                type="button"
                className={`nav-button ${activeTab === tab.id ? "active" : ""}`}
                onClick={() => setActiveTab(tab.id)}
              >
                {tab.label}
              </button>
            ))}
          </div>

          <div className="sidebar-card">
            <p className="eyebrow">Quick filters</p>
            <label className="field-label">
              Search catalog
              <input
                value={searchText}
                onChange={(event) => setSearchText(event.target.value)}
                placeholder="COSC 111, calculus, systems..."
              />
            </label>

            <label className="field-label">
              Course level
              <select
                value={selectedLevel}
                onChange={(event) => setSelectedLevel(event.target.value)}
              >
                {levels.map((level) => (
                  <option key={level.value || "all"} value={level.value}>
                    {level.label}
                  </option>
                ))}
              </select>
            </label>
          </div>

          <div className="sidebar-card">
            <p className="eyebrow">Status</p>
            <p className="status-copy">
              {loadingProfile ? "Loading profile..." : `${courses.length} courses ready`}
            </p>
            {error ? <p className="form-error">{error}</p> : null}
          </div>
        </aside>

        <section className="content-area">
          {activeTab === "advisor" ? <Chatbot token={token} user={user} /> : null}

          {activeTab === "catalog" ? (
            <section className="panel catalog-panel">
              <div className="panel-header">
                <div>
                  <p className="eyebrow">Catalog Explorer</p>
                  <h2>Course options you can actually browse</h2>
                  <p className="panel-subtext">
                    Search by code or title, or narrow by course level while you plan.
                  </p>
                </div>
              </div>

              {loadingCourses ? <p className="empty-state">Loading catalog...</p> : null}

              <div className="catalog-grid">
                {courses.map((course) => (
                  <article key={course.id} className="course-card">
                    <div className="course-topline">
                      <span className="course-code">{course.code}</span>
                      <span className="course-chip">{course.credits || "TBD"} credits</span>
                    </div>
                    <h3>{course.title}</h3>
                    <p>{course.description || "No description available yet."}</p>
                    <div className="course-meta">
                      <span>{course.department || "Department TBD"}</span>
                      <span>{course.semester_offered || "Semester TBD"}</span>
                      <span>{course.instructor || "Instructor TBD"}</span>
                    </div>
                  </article>
                ))}
              </div>

              {!loadingCourses && courses.length === 0 ? (
                <p className="empty-state">No courses matched the current filters.</p>
              ) : null}
            </section>
          ) : null}

          {activeTab === "profile" ? (
            <ProfilePanel
              user={user}
              courses={courses}
              degreeProgress={degreeProgress}
              onSave={handleSaveProfile}
              onSaveCompletedCourses={handleSaveCompletedCourses}
              onImportCompletedCourses={handleImportCompletedCourses}
              saving={savingProfile}
            />
          ) : null}
        </section>
      </main>
    </div>
  );
}

export default App;
