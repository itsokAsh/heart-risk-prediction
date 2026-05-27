import { useEffect, useState } from 'react';
import api from '../api/client';
import AssessmentCard from '../components/AssessmentCard';
import '../styles/dashboard.css';

function Dashboard() {
  const [assessments, setAssessments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    api.get('/assessments')
      .then((res) => {
        setAssessments(res.data || []);
      })
      .catch((err) => {
        setError(err.response?.data?.detail || 'Unable to load assessments');
      })
      .finally(() => setLoading(false));
  }, []);

  const handleDelete = async (id) => {
    try {
      await api.delete(`/assessments/${id}`);
      setAssessments((prev) => prev.filter((item) => item.id !== id));
    } catch (err) {
      setError(err.response?.data?.detail || 'Unable to delete assessment');
    }
  };

  return (
    <main className="page dashboard-page">
      <div className="container">
        <header className="page-header">
          <div>
            <p className="eyebrow">Your history</p>
            <h1>Assessment dashboard</h1>
            <p>Review your latest risk profiles and reports.</p>
          </div>
        </header>

        {error && <div className="error-banner">{error}</div>}

        {loading ? (
          <div className="loading-container">
            <div className="spinner spinner-large" />
            <span>Loading assessments…</span>
          </div>
        ) : assessments.length === 0 ? (
          <div className="empty-state">
            <h3>No assessments yet</h3>
            <p>Start your first assessment to see your report history here.</p>
          </div>
        ) : (
          <section className="dashboard-grid">
            {assessments.map((assessment) => (
              <AssessmentCard
                key={assessment.id}
                {...assessment}
                onDelete={handleDelete}
              />
            ))}
          </section>
        )}
      </div>
    </main>
  );
}

export default Dashboard;
