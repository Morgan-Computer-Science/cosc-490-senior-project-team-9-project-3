# Computer Science Audit Frontend Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Surface the new Computer Science audit interpretation in the existing profile and degree-progress UI so CS students can understand capstone readiness, pathway direction, and audit bucket progress directly in the product.

**Architecture:** Add a focused reusable CS audit summary component and render it in two places: the import preview and the persistent degree-progress area. Keep the UI conditional on `cs_audit_summary` so other majors stay unaffected and the page remains clean.

**Tech Stack:** React, existing frontend component structure, CSS in `App.css`, existing REST API payloads from the FastAPI backend.

---

## File Structure

**Create:**
- `frontend/src/components/CSAuditSummary.jsx` — reusable Computer Science audit summary component for import preview and persistent degree progress.

**Modify:**
- `frontend/src/components/ProfilePanel.jsx` — render the new CS audit summary in import preview and degree-progress sections.
- `frontend/src/App.css` — add styling for the new CS audit summary surfaces, readiness pills, grouped chips, and confirmation block.
- `frontend/src/api.js` — no API contract changes expected, but inspect only if payload handling needs a small defensive adjustment.

## Task 1: Add the Reusable CS Audit Summary Component

**Files:**
- Create: `frontend/src/components/CSAuditSummary.jsx`

- [ ] **Step 1: Create the CS audit summary component**

Create `frontend/src/components/CSAuditSummary.jsx`:

```jsx
const renderCourseGroup = (title, values = [], tone = "neutral") => {
  if (!values.length) {
    return null;
  }

  return (
    <div className={`cs-audit-group cs-audit-group-${tone}`}>
      <span className="cs-audit-group-label">{title}</span>
      <div className="remaining-list">
        {values.map((courseCode) => (
          <span key={`${title}-${courseCode}`} className={`course-chip cs-audit-chip cs-audit-chip-${tone}`}>
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
```

- [ ] **Step 2: Sanity-check the component structure manually**

Confirm the component:
- renders nothing when `summary` is absent
- supports `compact` mode for import preview
- does not depend on any new API calls

Expected: the file is self-contained and ready to be imported by `ProfilePanel.jsx`.

## Task 2: Render the CS Audit Summary in the Degree Progress Area

**Files:**
- Modify: `frontend/src/components/ProfilePanel.jsx`
- Create: `frontend/src/components/CSAuditSummary.jsx`

- [ ] **Step 1: Import the new component into `ProfilePanel.jsx`**

Add near the top of `frontend/src/components/ProfilePanel.jsx`:

```jsx
import CSAuditSummary from "./CSAuditSummary";
```

- [ ] **Step 2: Render the persistent CS audit summary in the degree-progress card**

Inside the degree-progress section of `ProfilePanel.jsx`, insert the component below the existing notes/advising text:

```jsx
          {degreeProgress?.cs_audit_summary ? (
            <CSAuditSummary
              summary={degreeProgress.cs_audit_summary}
              title="Your Computer Science standing"
            />
          ) : null}
```

- [ ] **Step 3: Verify the render conditions are safe**

Check that:
- non-CS majors still render normally
- the component appears only when `degreeProgress?.cs_audit_summary` exists
- no existing degree-progress content is removed

Expected: `ProfilePanel.jsx` stays backward compatible for all majors.

## Task 3: Render the CS Audit Summary in Import Preview

**Files:**
- Modify: `frontend/src/components/ProfilePanel.jsx`

- [ ] **Step 1: Find the import preview section**

Locate the block in `ProfilePanel.jsx` where `importPreview` is rendered.

Expected: this is where transcript/WebSIS/Canvas preview metadata and matched-course results are already displayed.

- [ ] **Step 2: Add the compact CS audit summary under the preview details**

Insert this block inside the import preview rendering path:

```jsx
              {importPreview?.cs_audit_summary ? (
                <CSAuditSummary
                  summary={importPreview.cs_audit_summary}
                  compact
                  title="Computer Science interpretation from this import"
                />
              ) : null}
```

- [ ] **Step 3: Keep the preview hierarchy clean**

Ensure the import preview still reads in this order:
- import metadata
- recognized completed/planned/remaining course codes
- CS audit interpretation (if present)
- apply / clear actions

Expected: the preview becomes richer without turning into a noisy debug panel.

## Task 4: Add Styling for the New CS Audit UI

**Files:**
- Modify: `frontend/src/App.css`

- [ ] **Step 1: Add the CS audit surface styles**

Append styling in `frontend/src/App.css` for the new summary component:

```css
.cs-audit-surface {
  margin-top: 18px;
  padding: 18px;
  border: 1px solid var(--line);
  border-radius: var(--radius-lg);
  background: color-mix(in srgb, var(--panel-soft) 78%, var(--panel) 22%);
  box-shadow: var(--shadow-soft);
}

.cs-audit-surface.compact {
  margin-top: 14px;
  padding: 16px;
}

.cs-audit-topline {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 14px;
}

.cs-audit-topline h4 {
  margin: 4px 0 0;
  font-size: 1rem;
}

.cs-audit-pill.status-ready {
  color: #166534;
  background: #dcfce7;
}

.cs-audit-pill.status-nearly_ready {
  color: #9a3412;
  background: #ffedd5;
}

.cs-audit-pill.status-not_ready {
  color: #991b1b;
  background: #fee2e2;
}

.cs-audit-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
  margin-top: 14px;
}

.cs-audit-card {
  padding: 14px;
  border: 1px solid var(--line);
  border-radius: var(--radius-md);
  background: var(--panel);
}

.cs-audit-card h5 {
  margin: 0 0 10px;
  font-size: 0.92rem;
}

.cs-audit-group + .cs-audit-group {
  margin-top: 10px;
}

.cs-audit-group-label {
  display: block;
  margin-bottom: 8px;
  color: var(--text-soft);
  font-size: 0.76rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.cs-audit-summary-lines {
  display: grid;
  gap: 8px;
  margin: 14px 0 0;
}

.cs-audit-summary-lines p {
  margin: 0;
  color: var(--text-soft);
  line-height: 1.55;
}

.cs-audit-callout {
  margin-top: 14px;
  padding: 14px;
  border-radius: var(--radius-md);
  border: 1px solid var(--line);
  background: var(--panel);
}

.cs-audit-callout strong {
  display: block;
  margin-bottom: 6px;
}

.cs-audit-callout p {
  margin: 0;
  color: var(--text-soft);
  line-height: 1.5;
}

.cs-audit-callout.warning {
  border-color: rgba(234, 88, 12, 0.2);
  background: rgba(255, 237, 213, 0.6);
}

.cs-audit-callout.pathway {
  border-color: rgba(0, 45, 98, 0.18);
}

.cs-audit-callout.confirmation {
  border-style: dashed;
}

.cs-audit-chip-complete {
  background: rgba(21, 128, 61, 0.12);
}

.cs-audit-chip-progress {
  background: rgba(2, 132, 199, 0.12);
}

.cs-audit-chip-remaining {
  background: rgba(148, 163, 184, 0.14);
}
```

- [ ] **Step 2: Add responsive fallback for smaller widths**

Append:

```css
@media (max-width: 920px) {
  .cs-audit-grid {
    grid-template-columns: 1fr;
  }
}
```

- [ ] **Step 3: Visually verify style consistency in the code**

Check that the new classes:
- reuse the current design tokens
- match the existing nested-panel/profile styles
- do not introduce a different visual language

Expected: the new UI feels native to the current product.

## Task 5: Run Frontend Verification

**Files:**
- Modify only as needed if verification exposes issues.

- [ ] **Step 1: Build the frontend**

Run:

```powershell
cd C:\Users\great\Desktop\cosc-490-senior-project-team-9-project-3\frontend
npm run build
```

Expected: Vite build succeeds with no new frontend errors.

- [ ] **Step 2: Manual reasoning pass against the requirements**

Check that the implementation now satisfies the spec:
- CS audit appears in import preview when `importPreview.cs_audit_summary` exists
- CS audit appears in degree progress when `degreeProgress.cs_audit_summary` exists
- capstone readiness is visually prominent
- summary lines are readable
- grouped progress sections are compact and understandable
- unmapped courses stay subordinate and honest

Expected: no extra routes, no chat clutter, no duplicated giant blocks.

- [ ] **Step 3: Commit the frontend CS audit surfacing work**

```powershell
git add frontend/src/components/CSAuditSummary.jsx frontend/src/components/ProfilePanel.jsx frontend/src/App.css docs/superpowers/specs/computer-science-audit-frontend-design.md docs/superpowers/plans/computer-science-audit-frontend-plan.md
git commit -m "Surface Computer Science audit depth in the student profile"
```

## Self-Review Notes

- Spec coverage: the plan covers import preview rendering, persistent degree-progress rendering, capstone readiness visibility, pathway direction, grouped course buckets, unmapped-course disclosure, and styling.
- Placeholder scan: no TODO/TBD language remains.
- Type consistency: all references use `cs_audit_summary`, which matches the backend payload added in the previous phase.
