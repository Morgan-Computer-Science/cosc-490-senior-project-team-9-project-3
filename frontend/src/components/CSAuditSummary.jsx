const renderCourseGroup = (title, values = [], tone = "neutral") => {
  if (!values?.length) {
    return null;
  }

  return (
    <div className={`cs-audit-group cs-audit-group-${tone}`}>
      <span className="cs-audit-group-label">{title}</span>
      <div className="remaining-list">
        {values.map((courseCode) => (
          <span
            key={`${title}-${courseCode}`}
            className={`course-chip cs-audit-chip cs-audit-chip-${tone}`}
          >
            {courseCode}
          </span>
        ))}
      </div>
    </div>
  );
};

const readinessLabel = {
  ready: "Ready for COSC490",
  nearly_ready: "Nearly ready for COSC490",
  not_ready: "Not ready for COSC490",
  unknown: "Capstone readiness unavailable",
};

const CSAuditSummary = ({ summary, compact = false, title = "Computer Science audit" }) => {
  if (!summary) {
    return null;
  }

  const readinessTone = summary.capstone_readiness?.status || "unknown";

  return (
    <section className={`cs-audit-surface ${compact ? "compact" : ""}`}>
      <div className="cs-audit-topline">
        <div>
          <p className="eyebrow">Computer Science Audit</p>
          <h4>{title}</h4>
        </div>
        <span className={`meta-pill cs-audit-pill status-${readinessTone}`}>
          {readinessLabel[readinessTone] || readinessLabel.unknown}
        </span>
      </div>

      {summary.capstone_readiness?.missing_foundations?.length ? (
        <div className="cs-audit-callout warning">
          <strong>Missing before capstone</strong>
          <p>{summary.capstone_readiness.missing_foundations.join(", ")}</p>
        </div>
      ) : null}

      {summary.summary_lines?.length ? (
        <div className="cs-audit-summary-lines">
          {summary.summary_lines.map((line) => (
            <p key={line}>{line}</p>
          ))}
        </div>
      ) : null}

      <div className="cs-audit-grid">
        <div className="cs-audit-card">
          <h5>Foundations</h5>
          {renderCourseGroup("Completed", summary.foundations?.completed, "complete")}
          {renderCourseGroup("In progress", summary.foundations?.in_progress, "progress")}
          {renderCourseGroup("Remaining", summary.foundations?.remaining, "remaining")}
        </div>

        <div className="cs-audit-card">
          <h5>Core progression</h5>
          {renderCourseGroup("Completed", summary.core_progress?.completed, "complete")}
          {renderCourseGroup("In progress", summary.core_progress?.in_progress, "progress")}
          {renderCourseGroup("Remaining", summary.core_progress?.remaining, "remaining")}
        </div>

        <div className="cs-audit-card">
          <h5>Math support</h5>
          {renderCourseGroup("Completed", summary.math_support?.completed, "complete")}
          {renderCourseGroup("In progress", summary.math_support?.in_progress, "progress")}
          {renderCourseGroup("Remaining", summary.math_support?.remaining, "remaining")}
        </div>

        <div className="cs-audit-card">
          <h5>Upper-level progress</h5>
          {renderCourseGroup("Completed", summary.upper_level_progress?.completed, "complete")}
          {renderCourseGroup("In progress", summary.upper_level_progress?.in_progress, "progress")}
          {renderCourseGroup("Remaining", summary.upper_level_progress?.remaining, "remaining")}
        </div>
      </div>

      {summary.pathway_direction?.primary_pathway ? (
        <div className="cs-audit-callout pathway">
          <strong>Current direction: {summary.pathway_direction.primary_pathway}</strong>
          {summary.pathway_direction.aligned_courses?.length ? (
            <p>Aligned courses: {summary.pathway_direction.aligned_courses.join(", ")}</p>
          ) : null}
          {summary.pathway_direction.notes ? <p>{summary.pathway_direction.notes}</p> : null}
        </div>
      ) : null}

      {summary.unmapped_courses?.length ? (
        <div className="cs-audit-callout confirmation">
          <strong>Needs advisor confirmation</strong>
          <p>{summary.unmapped_courses.join(", ")}</p>
        </div>
      ) : null}
    </section>
  );
};

export default CSAuditSummary;
