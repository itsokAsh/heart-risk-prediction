import { useEffect, useMemo, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import api from '../api/client';
import HealthForm from '../components/HealthForm';
import RiskResult from '../components/RiskResult';
import ReportDownload from '../components/ReportDownload';
import '../styles/assess.css';

function Assess() {
  const [searchParams] = useSearchParams();
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [debugInfo, setDebugInfo] = useState({ payload: null, response: null });

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
    setDebugInfo({ payload, response: null });
    try {
      const res = await api.post('/predict', payload);
      setResult(res.data);
      setDebugInfo({ payload, response: res.data });
    } catch (err) {
      setError(err.response?.data?.detail || 'Unable to run assessment');
    } finally {
      setLoading(false);
    }
  };

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
              <ReportDownload assessmentId={result?.id || assessmentId} />
            </>
          )}

          {(debugInfo.payload || debugInfo.response) && (
            <section className="debug-panel" aria-label="Debug payload and response">
              <h3>Debug panel</h3>
              <div className="debug-block">
                <span className="debug-label">Request payload</span>
                <pre>{JSON.stringify(debugInfo.payload, null, 2)}</pre>
              </div>
              <div className="debug-block">
                <span className="debug-label">Response</span>
                <pre>{JSON.stringify(debugInfo.response, null, 2)}</pre>
              </div>
            </section>
          )}
        </section>
      </div>
    </main>
  );
}

export default Assess;
