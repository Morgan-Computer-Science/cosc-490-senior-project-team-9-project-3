import { useEffect, useMemo, useState } from "react";

import { majorOptions } from "../majors";

const ProfilePanel = ({
  user,
  courses,
  degreeProgress,
  onSave,
  onSaveCompletedCourses,
  saving,
}) => {
  const [formData, setFormData] = useState({
    full_name: "",
    major: "",
    year: "",
  });
  const [completedCourseCodes, setCompletedCourseCodes] = useState([]);
  const [courseSearch, setCourseSearch] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    if (!user) {
      return;
    }

    setFormData({
      full_name: user.full_name ?? "",
      major: user.major ?? "",
      year: user.year ?? "",
    });
    setCompletedCourseCodes(
      (user.completed_courses ?? []).map((course) => course.course_code),
    );
  }, [user]);

  const filteredCourses = useMemo(() => {
    const search = courseSearch.trim().toLowerCase();
    if (!search) {
      return courses;
    }

    return courses.filter((course) =>
      `${course.code} ${course.title}`.toLowerCase().includes(search),
    );
  }, [courseSearch, courses]);

  const toggleCourse = (courseCode) => {
    setCompletedCourseCodes((current) =>
      current.includes(courseCode)
        ? current.filter((code) => code !== courseCode)
        : [...current, courseCode].sort(),
    );
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setMessage("");
    setError("");

    try {
      await onSave(formData);
      setMessage("Profile updated.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to update profile.");
    }
  };

  const handleCompletedCoursesSave = async () => {
    setMessage("");
    setError("");

    try {
      await onSaveCompletedCourses(completedCourseCodes);
      setMessage("Completed courses updated.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to update completed courses.");
    }
  };

  return (
    <section className="panel profile-panel">
      <div className="panel-header">
        <div>
          <p className="eyebrow">Student Profile</p>
          <h2>Keep the advisor grounded in your situation</h2>
        </div>
      </div>

      <div className="profile-summary">
        <div>
          <span className="summary-label">Email</span>
          <strong>{user?.email}</strong>
        </div>
        <div>
          <span className="summary-label">Joined</span>
          <strong>{user?.created_at ? new Date(user.created_at).toLocaleDateString() : "Unknown"}</strong>
        </div>
        <div>
          <span className="summary-label">Completed</span>
          <strong>{completedCourseCodes.length} courses tracked</strong>
        </div>
      </div>

      <div className="profile-grid">
        <form className="profile-form" onSubmit={handleSubmit}>
          {message ? <p className="form-success">{message}</p> : null}
          {error ? <p className="form-error">{error}</p> : null}

          <label>
            Full name
            <input
              type="text"
              value={formData.full_name}
              onChange={(event) =>
                setFormData((current) => ({ ...current, full_name: event.target.value }))
              }
            />
          </label>

          <label>
            Major
            <select
              value={formData.major}
              onChange={(event) =>
                setFormData((current) => ({ ...current, major: event.target.value }))
              }
            >
              <option value="">Select major</option>
              {majorOptions.map((major) => (
                <option key={major} value={major}>
                  {major}
                </option>
              ))}
            </select>
          </label>

          <label>
            Class year
            <select
              value={formData.year}
              onChange={(event) =>
                setFormData((current) => ({ ...current, year: event.target.value }))
              }
            >
              <option value="">Select year</option>
              <option value="Freshman">Freshman</option>
              <option value="Sophomore">Sophomore</option>
              <option value="Junior">Junior</option>
              <option value="Senior">Senior</option>
            </select>
          </label>

          <button type="submit" disabled={saving}>
            {saving ? "Saving..." : "Save profile"}
          </button>
        </form>

        <section className="progress-card">
          <p className="eyebrow">Degree Progress</p>
          <h3>{degreeProgress?.major || "Choose a major to track progress"}</h3>
          <p className="progress-percent">
            {degreeProgress?.completion_percent ?? 0}% complete
          </p>
          <p className="panel-subtext">
            {degreeProgress?.notes || "Degree requirement notes will appear here once a supported major is selected."}
          </p>
          <p className="panel-subtext">
            {degreeProgress?.advising_tips || "Add completed courses to see what is still left."}
          </p>

          <div className="remaining-list">
            {(degreeProgress?.recommended_next_courses ?? []).map((courseCode) => (
              <span key={`recommended-${courseCode}`} className="course-chip suggested-chip">
                Next: {courseCode}
              </span>
            ))}
            {(degreeProgress?.remaining_courses ?? []).slice(0, 8).map((courseCode) => (
              <span key={courseCode} className="course-chip remaining-chip">
                {courseCode}
              </span>
            ))}
            {!(degreeProgress?.remaining_courses ?? []).length ? (
              <span className="panel-subtext">No remaining required courses listed yet.</span>
            ) : null}
          </div>
        </section>
      </div>

      <section className="panel nested-panel completed-courses-panel">
        <div className="panel-header">
          <div>
            <p className="eyebrow">Completed Courses</p>
            <h3>Track what you have already finished</h3>
          </div>
          <button type="button" className="secondary-button" onClick={handleCompletedCoursesSave}>
            Save completed courses
          </button>
        </div>

        <label className="field-label">
          Search available courses
          <input
            value={courseSearch}
            onChange={(event) => setCourseSearch(event.target.value)}
            placeholder="Search by code or title..."
          />
        </label>

        <div className="completed-course-grid">
          {filteredCourses.map((course) => {
            const checked = completedCourseCodes.includes(course.code);
            return (
              <label
                key={course.id}
                className={`completed-course-card ${checked ? "checked" : ""}`}
              >
                <input
                  type="checkbox"
                  checked={checked}
                  onChange={() => toggleCourse(course.code)}
                />
                <div>
                  <strong>{course.code}</strong>
                  <p>{course.title}</p>
                </div>
              </label>
            );
          })}
        </div>
      </section>
    </section>
  );
};

export default ProfilePanel;
