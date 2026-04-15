const DegreeProgressView = ({ user, degreeProgress }) => {
  const recommended = degreeProgress?.recommended_next_courses ?? [];
  const blocked = degreeProgress?.blocked_courses ?? [];
  const remaining = degreeProgress?.remaining_courses ?? [];

  return (
    <section className="surface-stack">
      <section className="content-card">
        <div className="section-heading">
          <p className="section-kicker">Degree Progress</p>
          <h2>{degreeProgress?.major || user?.major || "Set your major to track progress"}</h2>
          <p>
            Track what is complete, what is ready next, and which courses are still blocked by prerequisite sequencing.
          </p>
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
        </div>
      </section>

      <section className="content-card">
        <div className="section-heading">
          <p className="section-kicker">Recommended Next Courses</p>
        </div>
        <div className="tag-list">
          {recommended.length ? recommended.map((code) => (
            <span key={code} className="tag-chip tag-chip-primary">{code}</span>
          )) : <p className="empty-note">No recommended next courses yet.</p>}
        </div>
      </section>

      <section className="content-card">
        <div className="section-heading">
          <p className="section-kicker">Blocked Courses</p>
        </div>
        <div className="tag-list">
          {blocked.length ? blocked.map((code) => (
            <span key={code} className="tag-chip tag-chip-warning">{code}</span>
          )) : <p className="empty-note">No blocked courses listed.</p>}
        </div>
      </section>

      <section className="content-card">
        <div className="section-heading">
          <p className="section-kicker">Remaining Requirements</p>
          <p>{degreeProgress?.notes || "Remaining required courses appear here as the profile becomes more complete."}</p>
        </div>
        <div className="tag-list">
          {remaining.length ? remaining.map((code) => (
            <span key={code} className="tag-chip">{code}</span>
          )) : <p className="empty-note">No remaining requirements listed yet.</p>}
        </div>
      </section>
    </section>
  );
};

export default DegreeProgressView;
