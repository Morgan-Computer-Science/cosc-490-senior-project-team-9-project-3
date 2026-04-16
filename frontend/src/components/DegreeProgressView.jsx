import { useMemo, useState } from "react";

import CSAuditSummary from "./CSAuditSummary";

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

const extractionMethodLabels = {
  text_local: "Direct text parse",
  pdf_local: "PDF text extraction",
  pdf_gemini: "Gemini PDF analysis",
  image_gemini: "Gemini image OCR",
  none: "No extraction",
};

const importSourceOptions = {
  websis_export: {
    title: "Degree audit or WebSIS export",
    helper: "Best for Degree Works, degree audits, or official academic-record PDFs.",
    action: "Preview audit import",
  },
  transcript_text: {
    title: "Transcript PDF or text",
    helper: "Best for transcript PDFs, pasted transcript text, or OCR text from a record.",
    action: "Preview transcript import",
  },
  manual: {
    title: "Manual course list",
    helper: "Best for a quick list of completed course codes you already know.",
    action: "Preview manual import",
  },
};

const DegreeProgressView = ({
  user,
  degreeProgress,
  onImportCompletedCourses,
  onSaveCompletedCourses,
  saving,
}) => {
  const [importSource, setImportSource] = useState("websis_export");
  const [importText, setImportText] = useState("");
  const [importFile, setImportFile] = useState(null);
  const [importPreview, setImportPreview] = useState(null);
  const [applying, setApplying] = useState(false);
  const [feedback, setFeedback] = useState("");
  const [error, setError] = useState("");

  const recommended = degreeProgress?.recommended_next_courses ?? [];
  const blocked = degreeProgress?.blocked_courses ?? [];
  const remaining = degreeProgress?.remaining_courses ?? [];
  const selectedSource = importSourceOptions[importSource] || importSourceOptions.websis_export;

  const completionSnapshot = useMemo(() => {
    const completed = degreeProgress?.completed_courses ?? [];
    return {
      completedCount: completed.length,
      remainingCount: remaining.length,
    };
  }, [degreeProgress, remaining.length]);

  const handlePreview = async () => {
    setFeedback("");
    setError("");
    try {
      const preview = await onImportCompletedCourses(importText, importFile, importSource);
      setImportPreview(preview);
      if (preview.completed_course_codes.length) {
        setFeedback(`Preview ready: ${preview.completed_course_codes.length} completed courses can be applied.`);
      } else {
        setFeedback("Preview ready. Review the recognition buckets before applying anything.");
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to preview this upload.");
    }
  };

  const handleApply = async () => {
    if (!importPreview?.completed_course_codes?.length) {
      return;
    }

    setApplying(true);
    setFeedback("");
    setError("");

    try {
      const existingCodes = (user?.completed_courses ?? []).map((course) => course.course_code);
      const merged = Array.from(new Set([...existingCodes, ...importPreview.completed_course_codes])).sort();
      await onSaveCompletedCourses(merged);
      setFeedback(`Applied ${importPreview.completed_course_codes.length} completed courses to degree progress.`);
      setImportPreview(null);
      setImportText("");
      setImportFile(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to apply completed courses.");
    } finally {
      setApplying(false);
    }
  };

  const handleClear = () => {
    setImportPreview(null);
    setImportText("");
    setImportFile(null);
    setFeedback("Import preview cleared.");
    setError("");
  };

  return (
    <section className="surface-stack">
      <section className="content-card degree-progress-hero">
        <div className="section-heading">
          <div>
            <p className="section-kicker">Degree Progress</p>
            <h2>{degreeProgress?.major || user?.major || "Set your major to track progress"}</h2>
            <p>
              Track what is complete, what is ready next, and which courses are still blocked by prerequisite sequencing.
            </p>
          </div>
          <div className="degree-progress-summary-note">
            <strong>Import Degree Works or a transcript PDF</strong>
            <span>Preview first, then apply only the completed courses you want to trust.</span>
          </div>
        </div>

        <div className="stat-grid">
          <article className="stat-card">
            <span className="stat-label">Completion</span>
            <strong>{degreeProgress?.completion_percent ?? 0}%</strong>
          </article>
          <article className="stat-card">
            <span className="stat-label">Ready Next</span>
            <strong>{recommended.length}</strong>
          </article>
          <article className="stat-card">
            <span className="stat-label">Blocked</span>
            <strong>{blocked.length}</strong>
          </article>
          <article className="stat-card">
            <span className="stat-label">Tracked Courses</span>
            <strong>{completionSnapshot.completedCount}</strong>
          </article>
        </div>
      </section>

      <section className="content-card degree-import-card">
        <div className="section-heading">
          <div>
            <p className="section-kicker">Import Degree Works</p>
            <h3>Update progress from a PDF without leaving this page</h3>
          </div>
          <span className="meta-pill">Preview first</span>
        </div>

        {feedback ? <p className="form-success">{feedback}</p> : null}
        {error ? <p className="form-error">{error}</p> : null}

        <div className="degree-import-layout">
          <div className="degree-import-form">
            <label className="field-label">
              Import type
              <select value={importSource} onChange={(event) => setImportSource(event.target.value)}>
                <option value="websis_export">Degree audit / WebSIS export</option>
                <option value="transcript_text">Transcript PDF or text</option>
                <option value="manual">Manual course list</option>
              </select>
            </label>

            <div className="import-source-guidance degree-guidance-card">
              <strong>{selectedSource.title}</strong>
              <p>{selectedSource.helper}</p>
            </div>

            <label className="field-label">
              Optional pasted text
              <textarea
                rows={4}
                value={importText}
                onChange={(event) => setImportText(event.target.value)}
                placeholder="Paste transcript text, Degree Works text, or a manual course list here if you want to supplement the PDF."
              />
            </label>

            <div className="bulk-entry-row import-row degree-import-actions">
              <label className="upload-button inline-upload-button">
                Choose PDF or text file
                <input
                  type="file"
                  accept=".pdf,.txt,.md,.csv,.json"
                  onChange={(event) => setImportFile(event.target.files?.[0] || null)}
                />
              </label>
              <button type="button" className="secondary-button" onClick={handlePreview} disabled={saving || applying}>
                {selectedSource.action}
              </button>
            </div>

            {importFile ? <p className="panel-subtext">Selected file: {importFile.name}</p> : null}
          </div>

          <div className="degree-import-help">
            <div className="degree-import-help-card">
              <span className="section-kicker">What happens</span>
              <ul>
                <li>We detect the document type.</li>
                <li>We separate completed, in-progress, and remaining signals.</li>
                <li>We only apply completed courses after your review.</li>
              </ul>
            </div>
            <div className="degree-import-help-card">
              <span className="section-kicker">Why this helps</span>
              <p>
                It gives you a cleaner degree-progress workflow than pasting everything into chat, while still keeping the advisor grounded in the same document.
              </p>
            </div>
          </div>
        </div>

        {importPreview ? (
          <div className="import-preview degree-import-preview">
            <p className="panel-subtext">
              {importPreview.source_summary} | Detected as {importDocumentLabels[importPreview.detected_document_type] || "Document"}
            </p>
            <div className="ocr-preview-meta">
              {importPreview.summary ? <p className="ocr-summary">{importPreview.summary}</p> : null}
              <div className="ocr-meta-badges">
                <span className="ocr-meta-badge">
                  {extractionMethodLabels[importPreview.extraction_method] || importPreview.extraction_method}
                </span>
                <span className="ocr-meta-badge">
                  {importDocumentLabels[importPreview.detected_document_type] || "Document"}
                </span>
              </div>
              {importPreview.confidence_note ? <p className="ocr-confidence-note">{importPreview.confidence_note}</p> : null}
              {importPreview.transcript_summary ? (
                <div className="degree-summary-strip">
                  {importPreview.transcript_summary.gpa ? <span className="meta-pill">GPA: {importPreview.transcript_summary.gpa}</span> : null}
                  {importPreview.transcript_summary.earned_credits ? <span className="meta-pill">Earned credits: {importPreview.transcript_summary.earned_credits}</span> : null}
                  {importPreview.transcript_summary.standing ? <span className="meta-pill">Standing: {importPreview.transcript_summary.standing}</span> : null}
                </div>
              ) : null}
            </div>

            <div className="import-preview-grid">
              <div className="import-preview-block">
                <span className="import-preview-label">Completed</span>
                <div className="tag-list">
                  {importPreview.completed_course_codes.length
                    ? importPreview.completed_course_codes.map((code) => <span key={`progress-complete-${code}`} className="tag-chip tag-chip-primary">{code}</span>)
                    : <p className="empty-note">No clearly completed courses recognized.</p>}
                </div>
              </div>
              <div className="import-preview-block">
                <span className="import-preview-label">Planned / Current</span>
                <div className="tag-list">
                  {importPreview.planned_course_codes.length
                    ? importPreview.planned_course_codes.map((code) => <span key={`progress-planned-${code}`} className="course-chip next-chip">{code}</span>)
                    : <p className="empty-note">No planned-course signals recognized.</p>}
                </div>
              </div>
              <div className="import-preview-block">
                <span className="import-preview-label">Remaining / Needed</span>
                <div className="tag-list">
                  {importPreview.remaining_course_codes.length
                    ? importPreview.remaining_course_codes.map((code) => <span key={`progress-remaining-${code}`} className="tag-chip tag-chip-warning">{code}</span>)
                    : <p className="empty-note">No remaining-course signals recognized.</p>}
                </div>
              </div>
              <div className="import-preview-block">
                <span className="import-preview-label">Needs confirmation</span>
                <div className="tag-list">
                  {importPreview.unknown_course_codes.length
                    ? importPreview.unknown_course_codes.map((code) => <span key={`progress-unknown-${code}`} className="course-chip remaining-chip">{code}</span>)
                    : <p className="empty-note">No unmatched course codes in this preview.</p>}
                </div>
              </div>
            </div>

            {importPreview.cs_audit_summary ? (
              <CSAuditSummary
                summary={importPreview.cs_audit_summary}
                compact
                title="Computer Science interpretation from this import"
              />
            ) : null}

            <div className="bulk-entry-row import-actions">
              <button type="button" className="secondary-button" onClick={handleApply} disabled={!importPreview.completed_course_codes.length || applying || saving}>
                {applying ? "Applying..." : "Apply completed courses"}
              </button>
              <button type="button" className="secondary-button" onClick={handleClear}>Clear preview</button>
            </div>
          </div>
        ) : null}
      </section>

      <section className="content-card">
        <div className="section-heading compact-heading">
          <div>
            <p className="section-kicker">Recommended Next Courses</p>
            <p>These are the strongest next moves based on your current tracked progress.</p>
          </div>
        </div>
        <div className="tag-list">
          {recommended.length ? recommended.map((code) => (
            <span key={code} className="tag-chip tag-chip-primary">{code}</span>
          )) : <p className="empty-note">No recommended next courses yet.</p>}
        </div>
      </section>

      <section className="content-card">
        <div className="section-heading compact-heading">
          <div>
            <p className="section-kicker">Blocked Courses</p>
            <p>These still need prerequisite work before they are realistic next steps.</p>
          </div>
        </div>
        <div className="tag-list">
          {blocked.length ? blocked.map((code) => (
            <span key={code} className="tag-chip tag-chip-warning">{code}</span>
          )) : <p className="empty-note">No blocked courses listed.</p>}
        </div>
      </section>

      <section className="content-card">
        <div className="section-heading compact-heading">
          <div>
            <p className="section-kicker">Remaining Requirements</p>
            <p>{degreeProgress?.notes || "Remaining required courses appear here as the profile becomes more complete."}</p>
          </div>
        </div>
        <div className="tag-list">
          {remaining.length ? remaining.map((code) => (
            <span key={code} className="tag-chip">{code}</span>
          )) : <p className="empty-note">No remaining requirements listed yet.</p>}
        </div>
        {degreeProgress?.cs_audit_summary ? (
          <CSAuditSummary summary={degreeProgress.cs_audit_summary} title="Your Computer Science standing" />
        ) : null}
      </section>
    </section>
  );
};

export default DegreeProgressView;
