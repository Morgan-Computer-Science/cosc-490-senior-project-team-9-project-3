import { useMemo } from "react";

const groupDepartments = (departments) => {
  const grouped = new Map();

  departments.forEach((department) => {
    const key = department.department || "General";
    const current = grouped.get(key) || {
      department: key,
      majors: [],
      overview: department.overview || "",
      office: department.office || "",
      email: department.email || "",
      phone: department.phone || "",
      school: department.school || "",
    };

    if (department.major && !current.majors.includes(department.major)) {
      current.majors.push(department.major);
    }

    if (!current.overview && department.overview) current.overview = department.overview;
    if (!current.office && department.office) current.office = department.office;
    if (!current.email && department.email) current.email = department.email;
    if (!current.phone && department.phone) current.phone = department.phone;
    if (!current.school && department.school) current.school = department.school;

    grouped.set(key, current);
  });

  return Array.from(grouped.values()).sort((left, right) => left.department.localeCompare(right.department));
};

const DepartmentsView = ({ departments, faculty, supportResources }) => {
  const groupedDepartments = useMemo(() => groupDepartments(departments), [departments]);

  return (
    <section className="surface-stack">
      <section className="content-card">
        <div className="section-heading">
          <div>
            <p className="section-kicker">Departments</p>
            <h2>Find the right academic home</h2>
          </div>
          <p>
            Browse cleaner department contacts, grouped programs, faculty expertise, and campus support services connected to the advising system.
          </p>
        </div>

        <div className="department-grid grouped-department-grid">
          {groupedDepartments.map((department) => (
            <article key={department.department} className="info-card department-card">
              <div className="info-card-header department-card-header">
                <div>
                  <h3>{department.department}</h3>
                  {department.school ? <p className="department-school">{department.school}</p> : null}
                </div>
                <span className="meta-pill department-count-pill">{department.majors.length || 1} program{department.majors.length === 1 ? "" : "s"}</span>
              </div>
              <p className="department-overview">{department.overview || "Department details are being added."}</p>
              {department.majors.length ? (
                <div className="department-pill-row">
                  {department.majors.map((major) => (
                    <span key={`${department.department}-${major}`} className="meta-pill department-pill">{major}</span>
                  ))}
                </div>
              ) : null}
              <div className="info-meta-list department-contact-list">
                {department.office ? <span>{department.office}</span> : null}
                {department.email ? <span>{department.email}</span> : null}
                {department.phone ? <span>{department.phone}</span> : null}
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
            <article key={member.email || member.name} className="info-card compact-card faculty-card">
              <div className="info-card-header">
                <h3>{member.name}</h3>
                <span className="meta-pill faculty-pill">{member.department}</span>
              </div>
              <p>{member.title}</p>
              <div className="info-meta-list faculty-meta-list">
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
};

export default DepartmentsView;
