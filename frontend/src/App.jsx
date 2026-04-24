import { startTransition, useDeferredValue, useEffect, useMemo, useState } from "react";

import "./App.css";
import {
  fetchConnectors,
  fetchCourses,
  fetchCurrentUser,
  fetchDegreeProgress,
  fetchDepartments,
  fetchFaculty,
  fetchSupportResources,
  importCompletedCourses,
  updateCompletedCourses,
  updateCurrentUser,
} from "./api";
import Chatbot from "./components/Chatbot.jsx";
import DegreeProgressView from "./components/DegreeProgressView.jsx";
import DepartmentsView from "./components/DepartmentsView.jsx";
import Login from "./components/Login.jsx";
import { majorOptions } from "./majors";
import ProfilePanel from "./components/ProfilePanel.jsx";
import SettingsView from "./components/SettingsView.jsx";
import Signup from "./components/Signup.jsx";

const levels = [
  { label: "All levels", value: "" },
  { label: "100 level", value: "1" },
  { label: "200 level", value: "2" },
  { label: "300 level", value: "3" },
  { label: "400 level", value: "4" },
];

const tabs = [
  {
    id: "advisor",
    label: "Advisor Chat",
    description: "Real-time academic planning with multimodal support",
  },
  {
    id: "catalog",
    label: "Course Catalog",
    description: "Search courses, instructors, and requirements",
  },
  {
    id: "departments",
    label: "Departments",
    description: "Find departments, faculty, and support resources",
  },
  {
    id: "progress",
    label: "Degree Progress",
    description: "Track completion, next courses, and blockers",
  },
  {
    id: "profile",
    label: "Profile",
    description: "Ground the advisor in your academic path",
  },
  {
    id: "settings",
    label: "Settings",
    description: "Account and future connector preferences",
  },
];

const renderNavIcon = (tabId) => {
  switch (tabId) {
    case "advisor":
      return (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="m3 9 9-7 9 7" />
          <path d="M5 10v10a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V10" />
          <path d="M9 22v-8h6v8" />
        </svg>
      );
    case "catalog":
      return (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1 0-5H20" />
        </svg>
      );
    case "departments":
      return (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
          <circle cx="9" cy="7" r="4" />
          <path d="M22 21v-2a4 4 0 0 0-3-3.87" />
          <path d="M16 3.13a4 4 0 0 1 0 7.75" />
        </svg>
      );
    case "progress":
      return (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M22 12h-4l-3 9L9 3l-3 9H2" />
        </svg>
      );
    case "profile":
      return (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2" />
          <circle cx="12" cy="7" r="4" />
        </svg>
      );
    default:
      return (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2Z" />
          <circle cx="12" cy="12" r="3" />
        </svg>
      );
  }
};

const App = () => {
  const [token, setToken] = useState(localStorage.getItem("token"));
  const [authView, setAuthView] = useState("login");
  const [activeTab, setActiveTab] = useState("advisor");
  const [themeMode, setThemeMode] = useState("light");
  const [user, setUser] = useState(null);
  const [courses, setCourses] = useState([]);
  const [departments, setDepartments] = useState([]);
  const [faculty, setFaculty] = useState([]);
  const [supportResources, setSupportResources] = useState([]);
  const [connectors, setConnectors] = useState([]);
  const [searchText, setSearchText] = useState("");
  const [selectedLevel, setSelectedLevel] = useState("");
  const [selectedMajor, setSelectedMajor] = useState("");
  const [loadingCourses, setLoadingCourses] = useState(false);
  const [loadingProfile, setLoadingProfile] = useState(false);
  const [savingProfile, setSavingProfile] = useState(false);
  const [degreeProgress, setDegreeProgress] = useState(null);
  const [error, setError] = useState("");
  const deferredSearch = useDeferredValue(searchText);
  const activeTabMeta = tabs.find((tab) => tab.id === activeTab);

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

    const loadReferenceData = async () => {
      try {
        const [departmentRows, facultyRows, supportRows] = await Promise.all([
          fetchDepartments(token),
          fetchFaculty(token),
          fetchSupportResources(token),
        ]);
        setDepartments(departmentRows);
        setFaculty(facultyRows);
        setSupportResources(supportRows);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load reference data.");
      }
    };

    loadReferenceData();
  }, [token]);

  useEffect(() => {
    if (!token) {
      return;
    }

    const loadConnectors = async () => {
      try {
        const connectorRows = await fetchConnectors(token);
        setConnectors(connectorRows);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load connector options.");
      }
    };

    loadConnectors();
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
          major: selectedMajor,
        });
        startTransition(() => setCourses(nextCourses));
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load courses.");
      } finally {
        setLoadingCourses(false);
      }
    };

    loadCourses();
  }, [token, deferredSearch, selectedLevel, selectedMajor]);

  const filteredDepartments = useMemo(() => {
    if (!searchText.trim()) {
      return departments;
    }
    const search = searchText.trim().toLowerCase();
    return departments.filter((department) =>
      `${department.department} ${department.major} ${department.overview}`.toLowerCase().includes(search),
    );
  }, [departments, searchText]);

  const filteredFaculty = useMemo(() => {
    if (!searchText.trim()) {
      return faculty;
    }
    const search = searchText.trim().toLowerCase();
    return faculty.filter((member) =>
      `${member.name} ${member.department} ${member.specialties}`.toLowerCase().includes(search),
    );
  }, [faculty, searchText]);

  const filteredSupport = useMemo(() => {
    if (!searchText.trim()) {
      return supportResources;
    }
    const search = searchText.trim().toLowerCase();
    return supportResources.filter((resource) =>
      `${resource.resource} ${resource.category} ${resource.details}`.toLowerCase().includes(search),
    );
  }, [supportResources, searchText]);

  const featuredCourses = useMemo(() => courses.slice(0, 6), [courses]);
  const compactCourses = useMemo(() => courses.slice(6), [courses]);

  const handleSignOut = () => {
    localStorage.removeItem("token");
    setToken(null);
    setUser(null);
    setCourses([]);
    setDepartments([]);
    setFaculty([]);
    setSupportResources([]);
    setSearchText("");
    setSelectedLevel("");
    setSelectedMajor("");
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

  const handleSaveCompletedCourses = async (courseCodes, importPreview = null) => {
    if (!token || !user) {
      throw new Error("You are signed out.");
    }
    setSavingProfile(true);
    try {
      const completedCourses = await updateCompletedCourses(token, courseCodes, importPreview);
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
    return authView === "login"
      ? <Login setToken={setToken} setView={setAuthView} />
      : <Signup setView={setAuthView} />;
  }

  return (
    <div className={`app-frame ${themeMode === "dark" ? "theme-dark" : ""}`}>
      <aside className="ms-sidebar">
        <div className="ms-sidebar-brand">
          <div className="brand-mark">M</div>
          <div className="brand-copy">
            <span>AI Advisor</span>
            <small>Morgan State</small>
          </div>
        </div>

        <nav className="ms-sidebar-nav">
          <div className="nav-group-title">Platform</div>
          {tabs.slice(0, 4).map((tab) => (
            <button
              key={tab.id}
              type="button"
              className={`shell-nav-link ${activeTab === tab.id ? "active" : ""}`}
              onClick={() => setActiveTab(tab.id)}
            >
              <span className="shell-nav-icon">{renderNavIcon(tab.id)}</span>
              <span className="shell-nav-copy">
                <strong>{tab.label}</strong>
              </span>
            </button>
          ))}

          <div className="nav-group-title account-group">Account</div>
          {tabs.slice(4).map((tab) => (
            <button
              key={tab.id}
              type="button"
              className={`shell-nav-link ${activeTab === tab.id ? "active" : ""}`}
              onClick={() => setActiveTab(tab.id)}
            >
              <span className="shell-nav-icon">{renderNavIcon(tab.id)}</span>
              <span className="shell-nav-copy">
                <strong>{tab.label}</strong>
              </span>
            </button>
          ))}
        </nav>

        <div className="ms-sidebar-footer">
          <button type="button" className="profile-footer-card" onClick={() => setActiveTab("profile")}>
            <div className="profile-avatar">
              {user?.full_name
                ? user.full_name.split(" ").map((part) => part[0]).join("").slice(0, 2).toUpperCase()
                : "MS"}
            </div>
            <div className="profile-footer-copy">
              <strong>{user?.full_name || "Morgan Student"}</strong>
              <span>{user?.major || "Major not set"}{user?.year ? `, ${user.year}` : ""}</span>
            </div>
          </button>
          <button type="button" className="sidebar-logout-button" onClick={handleSignOut}>
            Log out
          </button>
        </div>
      </aside>

      <main className="ms-main">
        <header className="ms-topbar">
          <div className="ms-search">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="11" cy="11" r="8" />
              <path d="m21 21-4.3-4.3" />
            </svg>
            <input
              type="text"
              placeholder="Search courses, faculty, or resources..."
              value={searchText}
              onChange={(event) => setSearchText(event.target.value)}
            />
            <div className="search-shortcut">
              <kbd>⌘</kbd>
              <kbd>K</kbd>
            </div>
          </div>

          <div className="topbar-actions">
            <button
              type="button"
              className="icon-button"
              title="Toggle theme"
              onClick={() => setThemeMode((current) => (current === "light" ? "dark" : "light"))}
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z" />
              </svg>
            </button>
            <button type="button" className="icon-button with-dot" title="Notifications">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9" />
                <path d="M10.3 21a1.94 1.94 0 0 0 3.4 0" />
              </svg>
            </button>
          </div>
        </header>

        <div className="ms-page">
          {activeTab === "advisor" && <Chatbot token={token} user={user} />}

          {activeTab === "catalog" && (
            <section className="surface-stack">
              <section className="content-card">
                <div className="section-heading">
                  <p className="section-kicker">Course Catalog</p>
                  <h2>Explore Morgan State courses</h2>
                  <p>Search by course title, code, or level while keeping the advisor connected to the same data.</p>
                </div>
                <div className="catalog-toolbar polished-toolbar">
                  <div className="catalog-toolbar-copy">
                    <strong>{loadingCourses ? "Refreshing catalog..." : `${courses.length} matching courses`}</strong>
                    <span>Browse by level without getting buried in one giant wall of cards.</span>
                  </div>
                  <div className="catalog-toolbar-controls">
                    <select value={selectedMajor} onChange={(event) => setSelectedMajor(event.target.value)}>
                      <option value="">All majors</option>
                      {majorOptions.map((major) => (
                        <option key={major} value={major}>{major}</option>
                      ))}
                    </select>
                    <select value={selectedLevel} onChange={(event) => setSelectedLevel(event.target.value)}>
                      {levels.map((level) => (
                        <option key={level.value || "all"} value={level.value}>{level.label}</option>
                      ))}
                    </select>
                    <span className="meta-pill">{selectedMajor || "All majors"}</span>
                    <span className="meta-pill">{selectedLevel ? `${selectedLevel}00 level` : "All levels"}</span>
                  </div>
                </div>
                {!courses.length ? (
                  <div className="catalog-empty-state">
                    <strong>No courses matched that filter.</strong>
                    <p>Try a different major core, clear the search, or switch back to all course levels.</p>
                  </div>
                ) : null}
                <div className="catalog-grid-light catalog-featured-grid">
                  {featuredCourses.map((course) => (
                    <article key={course.id} className="course-card-light">
                      <div className="course-card-top">
                        <span className="course-code-light">{course.code}</span>
                        <span className="meta-pill">{course.credits || "TBD"} credits</span>
                      </div>
                      <h3>{course.title}</h3>
                      <p className="course-card-summary">{course.description || "No description available yet."}</p>
                      <div className="info-meta-list course-card-footer">
                        <span>{course.department || "Department TBD"}</span>
                        <span>{course.semester_offered || "Semester TBD"}</span>
                        <span>{course.instructor || "Instructor TBD"}</span>
                      </div>
                    </article>
                  ))}
                </div>
                {compactCourses.length ? (
                  <section className="catalog-list-section">
                    <div className="section-heading compact-heading">
                      <div>
                        <p className="section-kicker">More Courses</p>
                        <h3>Keep browsing without the clutter</h3>
                      </div>
                    </div>
                    <div className="catalog-compact-list">
                      {compactCourses.map((course) => (
                        <article key={`compact-${course.id}`} className="catalog-compact-card">
                          <div className="catalog-compact-main">
                            <div className="catalog-compact-title">
                              <span className="course-code-light">{course.code}</span>
                              <strong>{course.title}</strong>
                            </div>
                            <p>{course.description || "No description available yet."}</p>
                          </div>
                          <div className="catalog-compact-meta">
                            <span>{course.credits || "TBD"} credits</span>
                            <span>{course.department || "Department TBD"}</span>
                            <span>{course.semester_offered || "Semester TBD"}</span>
                          </div>
                        </article>
                      ))}
                    </div>
                  </section>
                ) : null}
              </section>
            </section>
          )}

          {activeTab === "departments" && (
            <DepartmentsView
              departments={filteredDepartments}
              faculty={filteredFaculty}
              supportResources={filteredSupport}
            />
          )}

          {activeTab === "progress" && (
            <DegreeProgressView
              user={user}
              degreeProgress={degreeProgress}
              onImportCompletedCourses={handleImportCompletedCourses}
              onSaveCompletedCourses={handleSaveCompletedCourses}
              saving={savingProfile}
            />
          )}

          {activeTab === "profile" && (
            <ProfilePanel
              user={user}
              courses={courses}
              connectors={connectors}
              degreeProgress={degreeProgress}
              onSave={handleSaveProfile}
              onSaveCompletedCourses={handleSaveCompletedCourses}
              onImportCompletedCourses={handleImportCompletedCourses}
              onSignOut={handleSignOut}
              saving={savingProfile}
            />
          )}

          {activeTab === "settings" && <SettingsView user={user} />}
        </div>

        {error ? <div className="floating-error">{error}</div> : null}
      </main>
    </div>
  );
};

export default App;

