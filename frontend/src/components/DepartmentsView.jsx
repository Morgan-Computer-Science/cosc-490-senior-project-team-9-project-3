const DepartmentsView = ({ departments, faculty, supportResources }) => (
  <section className="surface-stack">
    <section className="content-card">
      <div className="section-heading">
        <p className="section-kicker">Departments</p>
        <h2>Find the right academic home</h2>
        <p>
          Browse department contacts, faculty expertise, and campus support services connected to the advising system.
        </p>
      </div>

      <div className="department-grid">
        {departments.map((department) => (
          <article key={department.department} className="info-card">
            <div className="info-card-header">
              <h3>{department.department}</h3>
              <span className="meta-pill">{department.major || "General"}</span>
            </div>
            <p>{department.overview}</p>
            <div className="info-meta-list">
              <span>{department.office}</span>
              <span>{department.email}</span>
              <span>{department.phone}</span>
            </div>
          </article>
        ))}
      </div>
    </section>

    <section className="content-card">
      <div className="section-heading">
        <p className="section-kicker">Faculty</p>
        <h2>People students can actually contact</h2>
      </div>
      <div className="department-grid">
        {faculty.map((member) => (
          <article key={member.email || member.name} className="info-card compact-card">
            <div className="info-card-header">
              <h3>{member.name}</h3>
              <span className="meta-pill">{member.department}</span>
            </div>
            <p>{member.title}</p>
            <div className="info-meta-list">
              <span>{member.email}</span>
              <span>{member.office}</span>
              <span>{member.office_hours}</span>
            </div>
          </article>
        ))}
      </div>
    </section>

    <section className="content-card">
      <div className="section-heading">
        <p className="section-kicker">Support</p>
        <h2>University help beyond course planning</h2>
      </div>
      <div className="support-grid">
        {supportResources.map((resource) => (
          <article key={resource.resource} className="support-card">
            <span className="meta-pill">{resource.category}</span>
            <h3>{resource.resource}</h3>
            <p>{resource.details}</p>
            <strong>{resource.contact}</strong>
          </article>
        ))}
      </div>
    </section>
  </section>
);

export default DepartmentsView;
