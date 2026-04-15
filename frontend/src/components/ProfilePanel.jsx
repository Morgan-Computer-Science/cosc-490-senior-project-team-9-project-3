import { useEffect, useMemo, useState } from "react";

import { majorOptions } from "../majors";

const ProfilePanel = ({
  user,
  courses,
  connectors,
  degreeProgress,
  onSave,
  onSaveCompletedCourses,
  onImportCompletedCourses,
  saving,
}) => {
  const [formData, setFormData] = useState({
    full_name: "",
    major: "",
    year: "",
  });
  const [completedCourseCodes, setCompletedCourseCodes] = useState([]);
  const [courseSearch, setCourseSearch] = useState("");
  const [bulkCourseInput, setBulkCourseInput] = useState("");
  const [importText, setImportText] = useState("");
  const [importFile, setImportFile] = useState(null);
  const [importSource, setImportSource] = useState("transcript_text");
  const [importPreview, setImportPreview] = useState(null);
  const [stagedImportCodes, setStagedImportCodes] = useState([]);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const importDocumentLabels = {
    transcript: "Transcript",
    degree_audit: "Degree audit",
    schedule: "Schedule",
    academic_form: "Academic form",
    image_screenshot: "Screenshot",
    pdf_document: "PDF",
    text_document: "Text document",
    generic_file: "File",
  };

  const connectorStatusLabels = {
    available: "Available now",
    upload_available: "Upload today",
    planned: "Planned",
  };

  const connectorStageLabels = {
    available_now: "Use directly in this workflow",
    upload_today_sync_later: "Upload-based now, direct sync later",
    planned_direct_sync: "Planned direct sync",
  };

  const extractionMethodLabels = {
    text_local: "Direct text parse",
    pdf_local: "PDF text extraction",
    pdf_gemini: "Gemini PDF analysis",
    image_gemini: "Gemini image OCR",
    none: "No extraction",
  };

  const importSourceDescriptions = {
    transcript_text: {
      title: "Transcript text",
      helper: "Best for pasted transcript lines, OCR text, or manual course-history notes.",
      placeholder: "Paste transcript text or academic history here...",
      action: "Preview transcript import",
    },
    manual: {
      title: "Manual course list",
      helper: "Best for a short list of course codes you already know you completed.",
      placeholder: "Paste course codes like COSC111, MATH141, ENGL101...",
      action: "Preview manual import",
    },
    canvas_export: {
      title: "Canvas-style export",
      helper: "Best for current-course dashboards, enrollment snapshots, and schedule-style exports.",
      placeholder: "Paste Canvas dashboard text, current courses, or upload a Canvas export...",
      action: "Preview Canvas import",
    },
    websis_export: {
      title: "WebSIS-style export",
      helper: "Best for official-looking course history, degree audit, or academic record exports.",
      placeholder: "Paste WebSIS course history, audit text, or upload an academic record export...",
      action: "Preview WebSIS import",
    },
  };

  const selectedImportSource = importSourceDescriptions[importSource] || importSourceDescriptions.manual;

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
    setImportPreview(null);
    setStagedImportCodes([]);
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

  const visibleRemainingCourses = useMemo(() => {
    const highlighted = new Set([
      ...(degreeProgress?.recommended_next_courses ?? []),
      ...(degreeProgress?.blocked_courses ?? []),
    ]);

    return (degreeProgress?.remaining_courses ?? []).filter(
      (courseCode) => !highlighted.has(courseCode),
    );
  }, [degreeProgress]);

  const toggleCourse = (courseCode) => {
    setCompletedCourseCodes((current) =>
      current.includes(courseCode)
        ? current.filter((code) => code !== courseCode)
        : [...current, courseCode].sort(),
    );
  };

  const handleBulkAdd = () => {
    const parsedCodes = bulkCourseInput
      .split(/[\s,;]+/)
      .map((code) => code.trim().toUpperCase())
      .filter(Boolean);

    if (!parsedCodes.length) {
      return;
    }

    setCompletedCourseCodes((current) =>
      Array.from(new Set([...current, ...parsedCodes])).sort(),
    );
    setBulkCourseInput("");
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

  const handleImportPreview = async () => {
    setMessage("");
    setError("");

    try {
      const preview = await onImportCompletedCourses(importText, importFile, importSource);
      setImportPreview(preview);
      setStagedImportCodes(preview.completed_course_codes);
      if (preview.completed_course_codes.length) {
        setMessage(`Preview ready: ${preview.completed_course_codes.length} recognized completed course(s) can be applied.`);
      } else if (preview.matched_course_codes.length) {
        setMessage("Preview ready. We recognized course codes, but not all of them look like completed classes.");
      } else {
        setMessage("No recognized Morgan course codes were found in that import.");
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to import completed courses.");
    }
  };

  const handleApplyImport = () => {
    if (!stagedImportCodes.length) {
      return;
    }

    setCompletedCourseCodes((current) =>
      Array.from(new Set([...current, ...stagedImportCodes])).sort(),
    );
    setStagedImportCodes([]);
    setMessage(`Applied ${importPreview?.completed_course_codes?.length ?? 0} recognized completed course(s) to your draft list.`);
  };

  const handleClearImport = () => {
    setImportPreview(null);
    setStagedImportCodes([]);
    setImportText("");
    setImportFile(null);
    setMessage("Import preview cleared.");
    setError("");
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
            {(degreeProgress?.blocked_courses ?? []).slice(0, 6).map((courseCode) => (
              <span key={`blocked-${courseCode}`} className="course-chip blocked-chip">
                Blocked: {courseCode}
              </span>
            ))}
            {visibleRemainingCourses.slice(0, 8).map((courseCode) => (
              <span key={courseCode} className="course-chip remaining-chip">
                {courseCode}
              </span>
            ))}
            {!visibleRemainingCourses.length &&
            !(degreeProgress?.recommended_next_courses ?? []).length &&
            !(degreeProgress?.blocked_courses ?? []).length ? (
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

        <div className="connector-surface">
          <div className="connector-surface-header">
            <div>
              <p className="eyebrow">Student Data Sources</p>
              <h4>Bring course history in from the right source</h4>
            </div>
            <span className="meta-pill">{connectors?.length || 0} connectors</span>
          </div>
          <p className="panel-subtext">
            Manual and OCR-assisted uploads work today. Canvas is positioned for current-course context, while WebSIS is positioned for official-record-style imports.
          </p>
          <div className="connector-grid">
            {(connectors ?? []).map((connector) => (
              <article key={connector.id} className="connector-card">
                <div className="connector-card-top">
                  <strong>{connector.display_name}</strong>
                  <span className={`connector-status status-${connector.status}`}>
                    {connectorStatusLabels[connector.status] || connector.status}
                  </span>
                </div>
                <p>{connector.description}</p>
                <div className="connector-meta">
                  <span>{connector.supports_file_upload ? "File upload supported" : "No file upload"}</span>
                  <span>{connector.requires_authentication ? "Auth required" : "No auth yet"}</span>
                </div>
                <div className="remaining-list connector-capabilities">
                  {(connector.capabilities ?? []).map((capability) => (
                    <span key={`${connector.id}-${capability}`} className="course-chip remaining-chip">
                      {capability.replaceAll("_", " ")}
                    </span>
                  ))}
                </div>
                <p className="panel-subtext connector-stage-note">
                  {connectorStageLabels[connector.launch_stage] || connector.launch_stage}
                </p>
              </article>
            ))}
          </div>
        </div>

        <label className="field-label">
          Bulk add course codes
          <div className="bulk-entry-row">
            <input
              value={bulkCourseInput}
              onChange={(event) => setBulkCourseInput(event.target.value)}
              placeholder="Example: COSC111 MATH141 ENGL101"
            />
            <button type="button" className="secondary-button" onClick={handleBulkAdd}>
              Add codes
            </button>
          </div>
        </label>

        <label className="field-label">
          Import from transcript text or file
          <div className="wizard-steps">
            <span className="wizard-step active">1. Choose source</span>
            <span className={`wizard-step ${importPreview ? "active" : ""}`}>2. Preview matches</span>
            <span className={`wizard-step ${stagedImportCodes.length ? "active" : ""}`}>3. Apply to draft</span>
            <span className="wizard-step">4. Save completed courses</span>
          </div>
          <select
            value={importSource}
            onChange={(event) => setImportSource(event.target.value)}
          >
            <option value="transcript_text">Transcript text</option>
            <option value="manual">Manual course list</option>
            <option value="canvas_export">Canvas-style export</option>
            <option value="websis_export">WebSIS-style export</option>
          </select>
          <div className="import-source-guidance">
            <strong>{selectedImportSource.title}</strong>
            <p>{selectedImportSource.helper}</p>
          </div>
          <textarea
            value={importText}
            onChange={(event) => setImportText(event.target.value)}
            placeholder={selectedImportSource.placeholder}
            rows={4}
          />
          <p className="panel-subtext">
            Upload now, direct sync later. The preview will interpret Canvas more like current enrollment context and WebSIS more like academic-record context.
          </p>
          <div className="bulk-entry-row import-row">
            <label className="upload-button inline-upload-button">
              Choose file
              <input
                type="file"
                accept=".pdf,.txt,.md,.csv,.json"
                onChange={(event) => setImportFile(event.target.files?.[0] || null)}
              />
            </label>
            <button type="button" className="secondary-button" onClick={handleImportPreview}>
              {selectedImportSource.action}
            </button>
          </div>
          {importFile ? (
            <p className="panel-subtext">Selected file: {importFile.name}</p>
          ) : null}
          {importPreview ? (
            <div className="import-preview">
              <p className="panel-subtext">
                {importPreview.source_summary} | {importPreview.matched_count} matched | Detected as {importDocumentLabels[importPreview.detected_document_type] || "Document"}
              </p>
              <div className="ocr-preview-meta">
                {importPreview.summary ? (
                  <p className="ocr-summary">{importPreview.summary}</p>
                ) : null}
                <div className="ocr-meta-badges">
                  <span className="ocr-meta-badge">
                    {extractionMethodLabels[importPreview.extraction_method] || importPreview.extraction_method}
                  </span>
                  <span className="ocr-meta-badge">
                    {importDocumentLabels[importPreview.detected_document_type] || "Document"}
                  </span>
                </div>
                {importPreview.confidence_note ? (
                  <p className="ocr-confidence-note">{importPreview.confidence_note}</p>
                ) : null}
              </div>
              <div className="import-preview-grid">
                <div className="import-preview-block">
                  <span className="import-preview-label">Completed</span>
                  {importPreview.completed_course_codes.length ? (
                    <div className="remaining-list">
                      {importPreview.completed_course_codes.map((courseCode) => (
                        <span key={`import-completed-${courseCode}`} className="course-chip suggested-chip">
                          {courseCode}
                        </span>
                      ))}
                    </div>
                  ) : (
                    <p className="panel-subtext">No clearly completed courses recognized.</p>
                  )}
                </div>

                <div className="import-preview-block">
                  <span className="import-preview-label">Planned / Current</span>
                  {importPreview.planned_course_codes.length ? (
                    <div className="remaining-list">
                      {importPreview.planned_course_codes.map((courseCode) => (
                        <span key={`import-planned-${courseCode}`} className="course-chip next-chip">
                          {courseCode}
                        </span>
                      ))}
                    </div>
                  ) : (
                    <p className="panel-subtext">No planned-course signals recognized.</p>
                  )}
                </div>

                <div className="import-preview-block">
                  <span className="import-preview-label">Remaining / Needed</span>
                  {importPreview.remaining_course_codes.length ? (
                    <div className="remaining-list">
                      {importPreview.remaining_course_codes.map((courseCode) => (
                        <span key={`import-remaining-${courseCode}`} className="course-chip blocked-chip">
                          {courseCode}
                        </span>
                      ))}
                    </div>
                  ) : (
                    <p className="panel-subtext">No remaining-course signals recognized.</p>
                  )}
                </div>
              </div>

              {importPreview.matched_course_codes.length ? (
                <p className="panel-subtext">
                  Recognized course codes overall: {importPreview.matched_course_codes.join(", ")}
                </p>
              ) : null}
              {importPreview.unknown_course_codes.length ? (
                <p className="panel-subtext">
                  Unmatched codes: {importPreview.unknown_course_codes.join(", ")}
                </p>
              ) : null}
              <div className="bulk-entry-row import-actions">
                <button
                  type="button"
                  className="secondary-button"
                  onClick={handleApplyImport}
                  disabled={!stagedImportCodes.length}
                >
                  Apply completed courses
                </button>
                <button type="button" className="secondary-button" onClick={handleClearImport}>
                  Clear preview
                </button>
              </div>
            </div>
          ) : null}
        </label>

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
