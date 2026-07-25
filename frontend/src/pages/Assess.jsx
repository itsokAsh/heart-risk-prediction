import { useEffect, useMemo, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import api from '../api/client';
import HealthForm from '../components/HealthForm';
import RiskResult from '../components/RiskResult';
import ReportDownload from '../components/ReportDownload';
import AiInsight from '../components/AiInsight';
import ChatWidget from '../components/ChatWidget';
import '../styles/assess.css';

function Assess() {
  const [searchParams] = useSearchParams();
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const assessmentId = useMemo(() => searchParams.get('id'), [searchParams]);

  useEffect(() => {
    if (!assessmentId) return;
    setLoading(true);
    setError('');
    api.get(`/assessments/${assessmentId}`)
      .then((res) => {
        setResult(res.data);
      })
      .catch((err) => {
        setError(err.response?.data?.detail || 'Unable to load assessment');
      })
      .finally(() => setLoading(false));
  }, [assessmentId]);

  const handleSubmit = async (payload) => {
    setLoading(true);
    setError('');
    setResult(null);
    try {
      const res = await api.post('/predict', payload);
      setResult(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Unable to run assessment');
    } finally {
      setLoading(false);
    }
  };

  const currentAssessmentId = result?.id || assessmentId;

  return (
    <main className="page assess-page">
      <div className="container assess-grid">
        <section className="assess-form-panel">
          <header className="page-header">
            <p className="eyebrow">New assessment</p>
            <h1>Clinical intake</h1>
            <p>Complete the intake to generate your personalized report.</p>
          </header>

          {error && <div className="error-banner">{error}</div>}

          <div className="card">
            <HealthForm onSubmit={handleSubmit} isSubmitting={loading} />
          </div>
        </section>

        <section className="assess-result-panel">
          {loading && !result ? (
            <div className="loading-container">
              <div className="spinner spinner-large" />
              <span>Analyzing your profile…</span>
            </div>
          ) : (
            <>
              <RiskResult result={result} />
              <AiInsight assessmentId={currentAssessmentId} />
              <ReportDownload assessmentId={currentAssessmentId} />
            </>
          )}

        </section>
      </div>

      {/* Floating AI Chat — only visible after a result */}
      <ChatWidget assessmentId={currentAssessmentId} />
    </main>
  );
}

export default Assess;

