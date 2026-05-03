const SettingsView = ({ user }) => (
  <section className="surface-stack">
    <section className="content-card">
      <div className="section-heading">
        <p className="section-kicker">Settings</p>
        <h2>Account and advisor preferences</h2>
        <p>
          This space is reserved for launch-facing account controls, notification preferences, and future connector settings.
        </p>
      </div>
      <div className="settings-grid">
        <article className="info-card">
          <div className="info-card-header">
            <h3>Account</h3>
            <span className="meta-pill">Current</span>
          </div>
          <p>{user?.full_name || "Student"}</p>
          <div className="info-meta-list">
            <span>{user?.email}</span>
            <span>{user?.major || "Major not set"}</span>
            <span>{user?.year || "Year not set"}</span>
          </div>
        </article>
        <article className="info-card">
          <div className="info-card-header">
            <h3>Planned settings</h3>
            <span className="meta-pill">Upcoming</span>
          </div>
          <p>Notification preferences, connector linking, accessibility controls, and account security options can live here next.</p>
        </article>
      </div>
    </section>
  </section>
);

export default SettingsView;
