import { useState, useEffect } from 'react';
import api from '../api/client';

function AiInsight({ assessmentId }) {
  const [insight, setInsight] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [hasFetched, setHasFetched] = useState(false);

  useEffect(() => {
    if (!assessmentId || hasFetched) return;

    setLoading(true);
    setError('');
    setHasFetched(true);

    api.post('/ai/explain', { assessment_id: assessmentId })
      .then((res) => {
        setInsight(res.data.explanation);
      })
      .catch((err) => {
        const detail = err.response?.data?.detail || '';
        if (err.response?.status === 503) {
          // Gemini not configured — gracefully hide
          setError('');
          setInsight('');
        } else {
          setError(detail || 'Unable to generate AI insight.');
        }
      })
      .finally(() => setLoading(false));
  }, [assessmentId, hasFetched]);

  // Don't render anything if no API key or no assessment
  if (!assessmentId || (!loading && !insight && !error)) return null;

  return (
    <div className="ai-insight-panel">
      <div className="ai-insight-header">
        <span className="ai-insight-icon">✨</span>
        <h3 className="ai-insight-title">AI Health Insight</h3>
        <span className="ai-insight-badge">Groq AI</span>
      </div>

      {loading && (
        <div className="ai-insight-loading">
          <div className="ai-insight-shimmer" />
          <div className="ai-insight-shimmer short" />
          <div className="ai-insight-shimmer" />
        </div>
      )}

      {error && (
        <p className="ai-insight-error">{error}</p>
      )}

      {insight && (
        <div className="ai-insight-content">
          {insight.split('\n').filter(Boolean).map((paragraph, idx) => (
            <p key={idx}>{paragraph}</p>
          ))}
        </div>
      )}

      <p className="ai-insight-disclaimer">
        This AI-generated insight is for educational purposes only and does not
        constitute medical advice. Always consult your physician.
      </p>
    </div>
  );
}

export default AiInsight;
