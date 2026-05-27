import { useState } from 'react';
import GaugeChart from './GaugeChart';

const CATEGORY_ICONS = {
  lifestyle: '🏃',
  diet: '🥗',
  medical: '🩺',
  stress: '🧘',
  monitoring: '📊',
  exercise: '💪',
  weight: '⚖️',
  smoking: '🚭',
  alcohol: '🍷',
  sleep: '😴',
  default: '💡'
};

function getCategoryIcon(category) {
  if (!category) return CATEGORY_ICONS.default;
  const lower = category.toLowerCase();
  for (const [key, icon] of Object.entries(CATEGORY_ICONS)) {
    if (lower.includes(key)) return icon;
  }
  return CATEGORY_ICONS.default;
}

function RiskResult({ result }) {
  const [expandedIdx, setExpandedIdx] = useState(null);

  if (!result) return null;

  const { risk_score, risk_level, recommendations } = result;
  const isHighRisk = risk_score > 50;

  const toggleExpand = (idx) => {
    setExpandedIdx((prev) => (prev === idx ? null : idx));
  };

  return (
    <div className="risk-result">
      {/* Gauge */}
      <GaugeChart riskScore={risk_score} />

      {/* Risk Banner */}
      <div className={`risk-banner ${isHighRisk ? 'high-risk' : 'low-risk'}`}>
        <div className="risk-banner-icon">
          {isHighRisk ? '⚠️' : '✅'}
        </div>
        <h2 className="risk-banner-title" id="risk-result-title">
          {isHighRisk ? 'High Risk Alert' : 'Lower Risk Assessment'}
        </h2>
        <p className="risk-banner-text">
          {isHighRisk
            ? `Your heart disease risk score is ${Math.round(risk_score)}%. This indicates a higher likelihood of cardiovascular disease. Please consult with a healthcare professional promptly for a comprehensive evaluation and personalized treatment plan.`
            : `Your heart disease risk score is ${Math.round(risk_score)}%. This indicates a lower likelihood of cardiovascular disease. Continue maintaining a healthy lifestyle and schedule regular check-ups with your healthcare provider.`}
        </p>
      </div>

      {/* Recommendations */}
      {recommendations && recommendations.length > 0 && (
        <section className="recommendations-section">
          <h3 className="recommendations-title">
            📋 Personalized Recommendations
          </h3>
          {recommendations.map((rec, idx) => {
            const isExpanded = expandedIdx === idx;
            const icon = getCategoryIcon(rec.category);

            return (
              <div className="recommendation-item" key={idx}>
                <button
                  className="recommendation-header"
                  id={`recommendation-toggle-${idx}`}
                  onClick={() => toggleExpand(idx)}
                  type="button"
                  aria-expanded={isExpanded}
                >
                  <span className="recommendation-icon">{icon}</span>
                  <span>{rec.category || rec.title || `Recommendation ${idx + 1}`}</span>
                  <span className={`recommendation-chevron ${isExpanded ? 'expanded' : ''}`}>
                    ▼
                  </span>
                </button>
                <div className={`recommendation-body ${isExpanded ? 'expanded' : ''}`}>
                  {rec.advice && (
                    <p className="recommendation-advice">{rec.advice}</p>
                  )}
                  {rec.steps && rec.steps.length > 0 && (
                    <ul className="recommendation-steps">
                      {rec.steps.map((s, sIdx) => (
                        <li key={sIdx}>{s}</li>
                      ))}
                    </ul>
                  )}
                  {!rec.advice && !rec.steps && rec.text && (
                    <p className="recommendation-advice">{rec.text}</p>
                  )}
                </div>
              </div>
            );
          })}
        </section>
      )}
    </div>
  );
}

export default RiskResult;
