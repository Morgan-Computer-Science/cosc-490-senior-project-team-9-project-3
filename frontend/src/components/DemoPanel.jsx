const demoScenarios = [
  {
    title: "Transcript Upload",
    summary: "Show how uploaded completed courses sharpen the advisor's next-course recommendations.",
    steps: [
      "Open Advisor and upload a transcript-style text file or PDF.",
      "Ask what you should take next.",
      "Point out that completed classes influence the recommendation list.",
    ],
  },
  {
    title: "Schedule Review",
    summary: "Show multimodal planning with prerequisite and course-load awareness.",
    steps: [
      "Upload a schedule screenshot or schedule text file.",
      "Ask whether the term looks realistic.",
      "Call out readiness, core-course alignment, and total-load reasoning.",
    ],
  },
  {
    title: "Degree Audit Review",
    summary: "Compare uploaded audit language against the app's own degree-progress view.",
    steps: [
      "Upload a degree-audit style file.",
      "Ask what still seems incomplete or what should happen next.",
      "Show that the advisor can talk about remaining requirements more concretely.",
    ],
  },
];

const capabilityCards = [
  {
    eyebrow: "RAG",
    title: "Morgan-grounded retrieval",
    body: "Answers are grounded in courses, departments, faculty contacts, degree requirements, and support resources instead of pure free-form generation.",
  },
  {
    eyebrow: "Multimodal",
    title: "Text, voice, and file-assisted advising",
    body: "Students can type, speak, or upload transcripts, schedules, screenshots, and audits to give the advisor more useful evidence.",
  },
  {
    eyebrow: "Planning",
    title: "Progress-aware recommendations",
    body: "The advisor tracks completed work, surfaces next courses, and flags blocked sequencing instead of acting like a generic chatbot.",
  },
];

const DemoPanel = () => (
  <section className="panel demo-panel">
    <div className="panel-header">
      <div>
        <p className="eyebrow">Demo Flow</p>
        <h2>Tell the story of the system clearly</h2>
        <p className="panel-subtext">
          Use this view during your presentation to walk from student context to retrieval, planning, and multimodal advising.
        </p>
      </div>
    </div>

    <div className="demo-grid">
      {capabilityCards.map((card) => (
        <article key={card.title} className="demo-capability-card">
          <p className="eyebrow">{card.eyebrow}</p>
          <h3>{card.title}</h3>
          <p>{card.body}</p>
        </article>
      ))}
    </div>

    <div className="demo-scenario-list">
      {demoScenarios.map((scenario, index) => (
        <article key={scenario.title} className="demo-scenario-card">
          <div className="demo-step-badge">0{index + 1}</div>
          <div className="demo-scenario-copy">
            <h3>{scenario.title}</h3>
            <p>{scenario.summary}</p>
            <ol className="demo-step-list">
              {scenario.steps.map((step) => (
                <li key={step}>{step}</li>
              ))}
            </ol>
          </div>
        </article>
      ))}
    </div>
  </section>
);

export default DemoPanel;
