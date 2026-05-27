import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import '../styles/landing.css';

function Landing() {
  const { isAuthenticated } = useAuth();

  return (
    <main className="page landing-page">
      <section className="landing-hero">
        <div className="landing-hero-bg" aria-hidden="true" />
        <div className="container landing-hero-grid">
          <div className="landing-hero-copy">
            <span className="eyebrow">Clinical editorial assessment</span>
            <h1 className="landing-hero-title">
              Calm, clear heart risk insights
              <span className="landing-hero-title-accent"> without the noise.</span>
            </h1>
            <p className="landing-hero-subtitle">
              HeartGuard evaluates 13 clinical factors to generate a nuanced risk profile,
              personalized guidance, and downloadable reports in minutes.
            </p>
            <div className="landing-hero-cta">
              {isAuthenticated ? (
                <Link className="btn-primary" to="/assess">
                  Start assessment
                </Link>
              ) : (
                <>
                  <Link className="btn-primary" to="/register">
                    Create an account
                  </Link>
                  <Link className="btn-secondary" to="/login">
                    Sign in
                  </Link>
                </>
              )}
            </div>
            <div className="landing-hero-tags">
              <span>PDF reports</span>
              <span>8 languages</span>
              <span>Clinician-ready</span>
            </div>
          </div>

          <div className="landing-hero-panel">
            <div className="hero-panel-card">
              <div className="hero-panel-header">
                <span className="hero-panel-eyebrow">Assessment preview</span>
                <span className="hero-panel-chip">Live model</span>
              </div>
              <h3 className="hero-panel-title">Risk profile summary</h3>
              <p className="hero-panel-text">
                A balanced overview with clear thresholds, lifestyle guidance, and clinical next steps.
              </p>
              <div className="hero-panel-stats">
                <div>
                  <span className="stat-label">Median completion</span>
                  <span className="stat-value">4:12</span>
                </div>
                <div>
                  <span className="stat-label">Risk tiers</span>
                  <span className="stat-value">Low / Moderate / High</span>
                </div>
                <div>
                  <span className="stat-label">Reports</span>
                  <span className="stat-value">PDF + Audio</span>
                </div>
              </div>
            </div>
            <div className="hero-panel-card muted">
              <h4>Designed for calm decision making</h4>
              <p>
                Every data point is translated into human guidance, so you know what to do next.
              </p>
            </div>
          </div>
        </div>
      </section>

      <section className="landing-features">
        <div className="container">
          <div className="section-header">
            <p className="eyebrow">What you get</p>
            <h2>Signal over noise</h2>
            <p className="section-subtitle">
              An experience that feels like a premium clinical report, not a tech demo.
            </p>
          </div>
          <div className="features-grid">
            <article className="feature-card">
              <h3>Structured intake</h3>
              <p>Multi-step form design keeps the focus on one clinical group at a time.</p>
            </article>
            <article className="feature-card">
              <h3>Guided recommendations</h3>
              <p>Actionable guidance grouped by lifestyle, monitoring, and clinical next steps.</p>
            </article>
            <article className="feature-card">
              <h3>Export-ready reports</h3>
              <p>Generate PDF and audio summaries for follow-up conversations.</p>
            </article>
          </div>
        </div>
      </section>

      <section className="landing-steps">
        <div className="container steps-grid">
          <div className="steps-copy">
            <p className="eyebrow">How it works</p>
            <h2>Three calm steps.</h2>
            <p>
              Capture clinical data, run the model, and walk away with a clear plan.
            </p>
          </div>
          <div className="steps-list">
            <div className="step-card">
              <span className="step-number">01</span>
              <h3>Enter clinical metrics</h3>
              <p>Input the 13 evidence-based factors in a guided format.</p>
            </div>
            <div className="step-card">
              <span className="step-number">02</span>
              <h3>Review your risk tier</h3>
              <p>Gauge-based visualization highlights low, moderate, or high risk.</p>
            </div>
            <div className="step-card">
              <span className="step-number">03</span>
              <h3>Download the report</h3>
              <p>Share a PDF or audio recap for follow-up and accountability.</p>
            </div>
          </div>
        </div>
      </section>
    </main>
  );
}

export default Landing;
